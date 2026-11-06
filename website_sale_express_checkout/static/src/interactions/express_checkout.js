/** @odoo-module **/
import { CustomerAddress } from '@portal/interactions/address';
import { patch } from '@web/core/utils/patch';
import { rpc } from '@web/core/network/rpc';

// Address fields whose completion triggers the delivery-method rating.
const DELIVERY_ADDRESS_FIELDS = ['street', 'city', 'zip', 'state_id'];
const CUIT_LENGTH = 11;

// Extends the native portal.customer_address interaction (which already handles
// the submit to data-submit-url, error rendering and the AR state loading) with
// the express-checkout specifics: the Factura A flow (CUIT validation + live ARCA
// lookup) and the on-page delivery-method rating. Guarded by the express nodes so
// the patch is inert on /my/address and /shop/address.
patch(CustomerAddress.prototype, {

    setup() {
        super.setup();
        this.expressForm = this.addressForm?.classList.contains('o_express_checkout_form');
        if (!this.expressForm) {
            return;
        }
        const qs = (sel) => this.addressForm.querySelector(sel);
        // ---- Factura A ----
        this.facturaACheckbox = qs('#express_factura_a');
        this.facturaAFields = qs('#express_factura_a_fields');
        this.vatInput = qs('#express_vat');
        this.vatStatus = qs('#express_vat_status');
        this.vatMsg = qs('#express_vat_msg');
        this.faDetails = qs('#express_fa_details');
        // Consumidor Final document (shares name="vat" with the FA CUIT input).
        this.dniInput = qs('#express_dni');
        this.dniContainer = qs('#div_express_dni');
        this.faFields = {
            fa_responsibility: qs('#express_fa_responsibility'),
            fa_name: qs('#express_fa_name'),
            fa_street: qs('#express_fa_street'),
            fa_zip: qs('#express_fa_zip'),
            fa_city: qs('#express_fa_city'),
            fa_state_id: qs('#express_fa_state'),
        };
        if (this.facturaACheckbox) {
            // A user toggle never restores (that path is only for the initial load
            // of a server-prefilled Factura A); the change event's argument must not
            // leak into the `restore` parameter.
            this._boundFaToggle = () => this._onFacturaAToggle(false);
            this.facturaACheckbox.addEventListener('change', this._boundFaToggle);
        }
        if (this.vatInput) {
            this._boundCuitInput = this._onCuitInput.bind(this);
            this.vatInput.addEventListener('input', this._boundCuitInput);
            this._debouncedLookup = this.debounced(this._lookupPadron, 400);
        }
        if (this.facturaACheckbox) {
            // On load, restore a server-prefilled Factura A (came back after submit)
            // instead of re-querying ARCA.
            this._onFacturaAToggle(this.facturaACheckbox.checked);
        }
        // ---- Zip: at least 4 characters to proceed ----
        this.zipInput = qs('[name="zip"]');
        if (this.zipInput) {
            this._boundCheckZip = this._checkZip.bind(this);
            this.zipInput.addEventListener('input', this._boundCheckZip);
            this._checkZip();
        }
        // ---- Delivery: rate + enable the methods once the address is complete ----
        this.deliveryContainer = document.querySelector('#express_delivery_container');
        if (this.deliveryContainer) {
            this._boundRefreshDelivery = this.debounced(this._refreshDeliveryMethods, 600);
            this._deliveryFields = DELIVERY_ADDRESS_FIELDS
                .map((name) => qs(`[name="${name}"]`))
                .filter(Boolean);
            this._deliveryFields.forEach((el) => {
                el.addEventListener('change', this._boundRefreshDelivery);
                el.addEventListener('input', this._boundRefreshDelivery);
            });
        }
        // ---- Persist contact/document fields so the form survives navigation ----
        // The address fields already persist through the delivery rating above; the
        // contact + DNI fields save through their own lightweight endpoint.
        this._boundPersist = this.debounced(this._persistForm, 700);
        this._persistFields = [
            qs('[name="name"]'), qs('[name="email"]'), qs('[name="phone"]'), this.dniInput,
        ].filter(Boolean);
        this._persistFields.forEach((el) => {
            el.addEventListener('change', this._boundPersist);
            el.addEventListener('input', this._boundPersist);
        });
    },

    destroy() {
        this.facturaACheckbox?.removeEventListener('change', this._boundFaToggle);
        this.vatInput?.removeEventListener('input', this._boundCuitInput);
        this.zipInput?.removeEventListener('input', this._boundCheckZip);
        this._deliveryFields?.forEach((el) => {
            el.removeEventListener('change', this._boundRefreshDelivery);
            el.removeEventListener('input', this._boundRefreshDelivery);
        });
        this._persistFields?.forEach((el) => {
            el.removeEventListener('change', this._boundPersist);
            el.removeEventListener('input', this._boundPersist);
        });
        super.destroy();
    },

    // ==================================================================
    // Factura A
    // ==================================================================
    // restore=true only on the initial load of a Factura A that came back
    // server-prefilled (after a submit): show the fiscal fields with their values
    // and lock the filled ones, WITHOUT re-querying ARCA.
    _onFacturaAToggle(restore = false) {
        const on = this.facturaACheckbox.checked;
        this.facturaAFields.classList.toggle('d-none', !on);
        this.vatInput.required = on;
        // Only the active document input is submitted (they share name="vat"):
        // FA -> CUIT enabled, DNI disabled; CF -> DNI enabled, CUIT disabled.
        this.vatInput.disabled = !on;
        if (this.dniInput) {
            this.dniInput.disabled = on;
            this.dniInput.required = !on;
            this.dniContainer?.classList.toggle('d-none', on);
        }
        if (!on) {
            // Back to Consumidor Final: clear everything, no fiscal fields, and
            // make sure the confirm button is not left disabled by a pending lookup.
            this.vatInput.value = '';
            this.vatInput.setCustomValidity('');
            this._setVatStatus('none');
            this.vatMsg?.classList.add('d-none');
            this._collapseFaDetails();
            this._clearFaFields();
            this._setSubmitEnabled(true);
        } else if (restore) {
            // Format the prefilled CUIT and lock the filled fiscal fields (empty
            // ones stay editable) — no ARCA call.
            this.vatInput.value = this._formatCuit(this.vatInput.value.replace(/\D/g, '').slice(0, CUIT_LENGTH));
            this.faDetails.classList.remove('d-none');
            Object.values(this.faFields).forEach((el) => {
                if (el) {
                    this._lockFaField(el, Boolean(el.value));
                }
            });
            this._setVatStatus('ok');
        } else {
            this._onCuitInput();
        }
    },

    _onCuitInput() {
        const digits = this.vatInput.value.replace(/\D/g, '').slice(0, CUIT_LENGTH);
        // Format as XX-XXXXXXXX-X while the buyer types or pastes.
        this.vatInput.value = this._formatCuit(digits);
        if (!this.facturaACheckbox.checked) {
            return;
        }
        // Not a full CUIT yet: keep the field invalid (blocks submit), no fiscal fields.
        if (digits.length < CUIT_LENGTH) {
            this._setVatStatus('none');
            this.vatMsg?.classList.add('d-none');
            this._collapseFaDetails();
            this._clearFaFields();
            this._setSubmitEnabled(true);
            this.vatInput.setCustomValidity(digits.length ? 'CUIT incompleto.' : '');
            return;
        }
        // Full CUIT: validate the check digit before hitting ARCA.
        if (!this._isValidCuit(digits)) {
            this._setVatStatus('error');
            this.vatMsg?.classList.remove('d-none');
            this._collapseFaDetails();
            this._clearFaFields();
            this._setSubmitEnabled(true);
            this.vatInput.setCustomValidity('El CUIT ingresado no es válido.');
            return;
        }
        // Valid CUIT: clear any previous result so a failing/empty response can't
        // leave stale data, disable the confirm button while ARCA is queried, then
        // spinner + lookup.
        this._clearFaFields();
        this._collapseFaDetails();
        this.vatMsg?.classList.add('d-none');
        this.vatInput.setCustomValidity('');
        this._setVatStatus('spinner');
        this._setSubmitEnabled(false);
        this._debouncedLookup(digits);
    },

    _formatCuit(digits) {
        if (digits.length <= 2) {
            return digits;
        }
        if (digits.length <= 10) {
            return `${digits.slice(0, 2)}-${digits.slice(2)}`;
        }
        return `${digits.slice(0, 2)}-${digits.slice(2, 10)}-${digits.slice(10)}`;
    },

    // Enable/disable the checkout confirm button(s) — used to block advancing
    // while the ARCA lookup is in flight. Bootstrap's .disabled on the <a> button
    // sets pointer-events:none, so the click (and its submit handler) can't fire.
    _setSubmitEnabled(enabled) {
        const buttons = this.submitButtons || document.getElementsByName('website_sale_main_button');
        Array.from(buttons).forEach((b) => b.classList.toggle('disabled', !enabled));
    },

    async _lookupPadron(cuit) {
        let res;
        try {
            res = await this.waitFor(rpc('/shop/express_checkout/padron_lookup', { vat: cuit }));
        } catch {
            res = null;
        }
        // Ignore a stale response if the CUIT changed meanwhile.
        if (this.vatInput.value.replace(/\D/g, '') !== cuit) {
            this._setSubmitEnabled(true);
            return;
        }
        // Always show the fiscal section with an editable+required baseline; then,
        // if ARCA answered, lock ONLY the fields it actually returned and leave the
        // ones it left empty editable so the buyer can complete them (Marco's
        // request: never leave an empty field disabled and blocking the checkout).
        this._showFaDetails(true);
        if (res && res.available && res.found && res.values) {
            this._setVatStatus('ok');
            this._fillFaFields(res.values);
        } else {
            // ARCA could not resolve the CUIT: manual entry, everything editable.
            this._setVatStatus('none');
        }
        // Re-enable the confirm button now that the lookup has resolved.
        this._setSubmitEnabled(true);
    },

    _setVatStatus(kind) {
        if (!this.vatStatus) {
            return;
        }
        const icons = {
            spinner: '<span class="fa fa-spinner fa-spin"/>',
            ok: '<span class="fa fa-check text-success"/>',
            error: '<span class="fa fa-times text-danger"/>',
        };
        this.vatStatus.innerHTML = icons[kind] || '';
        this.vatStatus.classList.toggle('d-none', !icons[kind]);
    },

    _collapseFaDetails() {
        this.faDetails?.classList.add('d-none');
        Object.values(this.faFields).forEach((el) => {
            if (el) {
                el.required = false;
            }
        });
    },

    // Show the fiscal section with an editable + required baseline. Fields ARCA
    // returns are locked afterwards, one by one, in _fillFaFields.
    _showFaDetails(editable) {
        this.faDetails.classList.remove('d-none');
        Object.values(this.faFields).forEach((el) => {
            if (el) {
                this._lockFaField(el, !editable);
            }
        });
    },

    // Lock (ARCA-provided, read-only/greyed) or unlock (buyer must fill, required)
    // a single fiscal field.
    _lockFaField(el, locked) {
        el.required = !locked;
        if (el.tagName === 'SELECT') {
            el.classList.toggle('pe-none', locked);
            el.classList.toggle('opacity-50', locked);
        } else {
            el.readOnly = locked;
            el.classList.toggle('bg-light', locked);
        }
    },

    _clearFaFields() {
        Object.values(this.faFields).forEach((el) => {
            if (!el) {
                return;
            }
            el.value = '';
            el.required = false;
            el.readOnly = false;
            el.classList.remove('bg-light', 'pe-none', 'opacity-50');
        });
    },

    // Per field: if ARCA returned a value, set it and lock the field; if it came
    // back empty, leave the field editable and required so the buyer completes it.
    _fillFaFields(values) {
        const apply = (el, v) => {
            if (!el) {
                return;
            }
            const value = v != null && v !== false ? String(v) : '';
            el.value = value;
            this._lockFaField(el, Boolean(value));
        };
        apply(this.faFields.fa_responsibility, values.l10n_ar_afip_responsibility_type_id);
        apply(this.faFields.fa_name, values.name);
        apply(this.faFields.fa_street, values.street);
        apply(this.faFields.fa_zip, values.zip);
        apply(this.faFields.fa_city, values.city);
        apply(this.faFields.fa_state_id, values.state_id);
    },

    _isValidCuit(digits) {
        if (digits.length !== CUIT_LENGTH) {
            return false;
        }
        const weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
        const sum = weights.reduce((acc, w, i) => acc + w * parseInt(digits[i], 10), 0);
        let check = 11 - (sum % 11);
        if (check === 11) {
            check = 0;
        } else if (check === 10) {
            check = 9;
        }
        return check === parseInt(digits[10], 10);
    },

    // The native interaction re-marks `vat` required for AR on every country change
    // (after our setup ran). Re-assert our Factura A state so the hidden CUIT is not
    // left required (which would silently fail form.reportValidity()).
    async _onChangeCountry(init = false) {
        await super._onChangeCountry(init);
        if (this.expressForm && this.vatInput) {
            this.vatInput.required = this.facturaACheckbox.checked;
            if (this.facturaACheckbox.checked) {
                this._onCuitInput();
            } else {
                this.vatInput.setCustomValidity('');
            }
        }
    },

    _checkZip() {
        const value = this.zipInput.value.trim();
        this.zipInput.setCustomValidity(
            value.length > 0 && value.length < 4
                ? 'El código postal debe tener al menos 4 caracteres.'
                : ''
        );
    },

    // ==================================================================
    // Persistence — keep the provisional partner in sync with the form
    // ==================================================================
    // Contact + address + CF document. The CUIT (Factura A) is intentionally not
    // persisted here: its billing partner is built at submit; when Factura A is on
    // the main document is left blank.
    _formPayload() {
        const val = (name) => this.addressForm.querySelector(`[name="${name}"]`)?.value?.trim() || '';
        return {
            name: val('name'),
            email: val('email'),
            phone: val('phone'),
            street: val('street'),
            city: val('city'),
            zip: val('zip'),
            state_id: val('state_id'),
            vat: this.facturaACheckbox?.checked ? '' : (this.dniInput?.value?.trim() || ''),
        };
    },

    async _persistForm() {
        await this.waitFor(rpc('/shop/express_checkout/save', this._formPayload()));
    },

    // ==================================================================
    // Delivery
    // ==================================================================
    async _refreshDeliveryMethods() {
        const payload = this._formPayload();
        if (payload.zip.replace(/\D/g, '').length < 4 || !payload.state_id) {
            return;
        }
        const res = await this.waitFor(rpc('/shop/express_checkout/delivery_methods', payload));
        if (res && res.delivery_form) {
            this.deliveryContainer.innerHTML = res.delivery_form;
            this._wireDeliveryMethods();
            await this._rateDeliveryMethods();
        }
    },

    _wireDeliveryMethods() {
        this.deliveryContainer.querySelectorAll('input[name="o_delivery_radio"]').forEach((radio) => {
            radio.addEventListener('change', () => this._selectDeliveryMethod(radio));
        });
    },

    _deliveryBadge(radio) {
        return radio.closest('[name="o_delivery_method"]')?.querySelector('[name="price"]');
    },

    async _rateDeliveryMethods() {
        const radios = this.deliveryContainer.querySelectorAll('input[name="o_delivery_radio"]');
        await Promise.all([...radios].map(async (radio) => {
            const badge = this._deliveryBadge(radio);
            try {
                const rate = await this.waitFor(rpc('/shop/get_delivery_rate', { dm_id: radio.dataset.dmId }));
                if (rate && rate.success) {
                    radio.disabled = false;
                    if (badge) {
                        badge.classList.remove('text-muted');
                        badge.innerHTML = rate.is_free_delivery ? 'Gratis' : (rate.amount_delivery || '');
                    }
                } else {
                    radio.disabled = true;
                    if (badge) {
                        badge.classList.add('text-muted');
                        badge.textContent = (rate && rate.error_message) || '';
                    }
                }
            } catch {
                radio.disabled = true;
            }
        }));
    },

    async _selectDeliveryMethod(radio) {
        if (radio.disabled) {
            return;
        }
        const res = await this.waitFor(rpc('/shop/set_delivery_method', { dm_id: radio.dataset.dmId }));
        const badge = this._deliveryBadge(radio);
        if (badge && res) {
            badge.innerHTML = res.is_free_delivery ? 'Gratis' : (res.amount_delivery || '');
        }
    },
});
