##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import json

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
from odoo.tools import str2bool

# Address fields the buyer fills; everything else in the payload is contact/tax.
_ADDRESS_FIELDS = ("street", "street2", "city", "zip", "state_id")
# Contact fields persisted (together with the address and CF document) on the
# provisional partner so the form survives navigating away and back.
_EXPRESS_CONTACT_FIELDS = ("name", "email", "phone")


class WebsiteSaleExpressCheckout(WebsiteSale):
    """One-page AR checkout.

    NOTE ON ROUTE COEXISTENCE: core already defines ``/shop/express_checkout`` as
    ``type='jsonrpc', methods=['POST']`` (Google/Apple Pay express flow,
    ``WebsiteSale.process_express_checkout``). Our render route below is
    ``type='http'`` GET, so both rules coexist in the routing map (matched by
    method) and the buyer-facing submit lives at ``/shop/express_checkout/submit``.

    The ``_parse_form_data`` / ``_complete_address_values`` /
    ``_get_mandatory_billing_address_fields`` overrides are merged into the global
    ``WebsiteSale`` controller, so they must be scoped to the express flow via the
    ``request.express_checkout_flow`` flag (set by the submit route). Outside that
    flow they defer entirely to super().
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _express_checkout_enabled(self, order_sudo):
        """The express flow is AR-only and opt-in per website (checked on the
        cart's company, not the user's — matches personalizations_adhoc)."""
        return bool(
            order_sudo and order_sudo.website_id.enable_express_checkout and order_sudo.company_id.country_code == "AR"
        )

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    @route(
        "/shop/express_checkout",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def express_checkout(self, **query_params):
        order_sudo = request.cart
        if redirection := self._check_cart(order_sudo):
            return request.redirect(redirection.location)
        if not self._express_checkout_enabled(order_sudo):
            # Module installed but disabled / non-AR company: fall back to native.
            return request.redirect("/shop/checkout")
        render_values = self._prepare_express_checkout_values(order_sudo, **query_params)
        return request.render("website_sale_express_checkout.express_checkout", render_values)

    def _prepare_express_checkout_values(self, order_sudo, **kwargs):
        # Reuse the native checkout page + address form values.
        values = self._prepare_checkout_page_values(order_sudo, **kwargs)
        # Prefill from the DELIVERY contact, not the order's main partner: this form
        # is the contact + shipping address. For Consumidor Final both are the same
        # partner; for Factura A the main partner is the billing one (razón social +
        # fiscal domicile), so prefilling from it would show the fiscal name/address
        # over the delivery fields (and risk shipping to the fiscal address on a
        # re-confirm). Anonymous cart -> blank form (the public user must not leak).
        if order_sudo._is_anonymous_cart():
            partner_sudo = request.env["res.partner"].sudo()
        else:
            partner_sudo = order_sudo.partner_shipping_id or order_sudo.partner_id
        values.update(
            self._prepare_address_form_values(
                partner_sudo,
                address_type="billing",
                use_delivery_as_billing=True,
                order_sudo=order_sudo,
                **kwargs,
            )
        )
        # The buyer takes no tax decision: hide the whole billing/b2b block (which
        # carries company_name, VAT and the ARCA responsibility select). The CUIT
        # for the Factura A path is rendered by the express page itself.
        values["is_used_as_billing"] = False
        # AR-only: default the (hidden) country to Argentina so the province field
        # renders (AR is state_required) and the interaction loads AR states. It is
        # also submitted, so country_id/state_id pass validation before the server
        # forces the country in _complete_address_values.
        ar_country = request.env.ref("base.ar")
        values["country"] = ar_country
        values["country_states"] = ar_country.state_ids
        # Responsibility options for the Factura A manual path (when ARCA can't be
        # reached, the buyer picks it themselves).
        values["express_responsibility_types"] = request.env["l10n_ar.afip.responsibility.type"].sudo().search([])
        # Restore the Factura A state when coming back to the page after a submit:
        # the billing partner (partner_invoice_id, separate from the delivery one
        # and carrying a CUIT) holds the fiscal data, so we re-check the box and
        # prefill the CUIT + fiscal fields without re-querying ARCA.
        billing_sudo = order_sudo.partner_invoice_id
        is_factura_a = bool(
            not order_sudo._is_anonymous_cart()
            and billing_sudo
            and billing_sudo != order_sudo.partner_shipping_id
            and billing_sudo.l10n_latam_identification_type_id == request.env.ref("l10n_ar.it_cuit")
        )
        values["express_factura_a"] = is_factura_a
        values["express_fa_billing"] = billing_sudo if is_factura_a else request.env["res.partner"].sudo()
        # delivery_form needs `delivery_methods` in context. We only list the
        # carriers; the rate is resolved client-side via the jsonrpc delivery
        # routes once the buyer enters an address (it cannot be computed here).
        if order_sudo._has_deliverable_products():
            values["delivery_methods"] = order_sudo._get_delivery_methods()
        # checkout_layout -> navigation_buttons needs the step nav values.
        values.update(request.website._get_checkout_step_values())
        return values

    # ------------------------------------------------------------------
    # Live ARCA padron lookup (Factura A)
    # ------------------------------------------------------------------
    @route(
        "/shop/express_checkout/padron_lookup",
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def express_checkout_padron_lookup(self, vat=None):
        """Look up the fiscal data of a CUIT in the ARCA padron.

        Thin route wrapper: the actual work lives in ``_express_padron_lookup``
        so the padron bridge can override the logic without re-decorating the
        route (and so tests can call it directly without the routing wrapper).

        :return: ``{"available": bool, "success": bool, "values": dict}``. When
                 ``available`` is False (or ``success`` is False), the client
                 renders the fiscal fields editable for manual entry.
        """
        return self._express_padron_lookup(vat)

    def _express_padron_lookup(self, vat=None):
        """Base module: ARCA is not available (no EE) -> manual entry.

        The ``website_sale_express_checkout_padron`` bridge overrides this to
        run the real query.
        """
        return {"available": False}

    # ------------------------------------------------------------------
    # Shared hooks — scoped to the express flow
    # ------------------------------------------------------------------
    def _parse_form_data(self, form_data):
        address_values, extra_form_data = super()._parse_form_data(form_data)
        if getattr(request, "express_checkout_flow", False) and not getattr(
            request, "express_checkout_factura_a", False
        ):
            # Consumidor Final: the responsibility is assigned server-side, so a
            # forged value is discarded. The id type is derived from the document
            # shape (DNI vs CUIT) — not trusted from the form — and set together
            # with the vat so the l10n_ar identification constraint validates
            # against the right type when the partner is written.
            address_values.pop("l10n_ar_afip_responsibility_type_id", None)
            vat = address_values.get("vat")
            if vat:
                digits = "".join(filter(str.isdigit, vat))
                id_xmlid = "l10n_ar.it_cuit" if len(digits) == 11 else "l10n_ar.it_dni"
                address_values["l10n_latam_identification_type_id"] = request.env.ref(id_xmlid).id
            else:
                address_values.pop("l10n_latam_identification_type_id", None)
        return address_values, extra_form_data

    # Fields that l10n_latam_base / l10n_ar force as mandatory for AR billing but
    # that this flow derives server-side (responsibility, id type) or does not ask
    # a Consumidor Final (vat). We relax them in the *consumers* of the mandatory
    # set — _validate_address_values (submit) and _check_billing_address (payment
    # gate) — instead of _get_mandatory_billing_address_fields, because those
    # localization overrides re-add the fields AFTER ours in the MRO, defeating a
    # discard there.
    _EXPRESS_DERIVED_FIELDS = frozenset(
        {
            "l10n_ar_afip_responsibility_type_id",
            "l10n_latam_identification_type_id",
        }
    )

    def _validate_address_values(self, address_values, *args, **kwargs):
        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values, *args, **kwargs
        )
        if not getattr(request, "express_checkout_flow", False):
            return invalid_fields, missing_fields, error_messages
        # Consumidor Final: responsibility + id type are derived server-side, so
        # they are relaxed. The document (vat/DNI) IS asked, so it is not relaxed.
        # Factura A carries all of them from the form (ARCA-verified or entered by
        # hand), so nothing is relaxed there.
        optional = set()
        if not getattr(request, "express_checkout_factura_a", False):
            optional = set(self._EXPRESS_DERIVED_FIELDS)
        had_missing = bool(missing_fields)
        invalid_fields = invalid_fields - optional
        missing_fields = missing_fields - optional
        if had_missing and not missing_fields:
            msg = request.env._("Some required fields are empty.")
            error_messages = [m for m in error_messages if m != msg]
        # Beyond the native "not empty" check, the zip must have at least 4
        # characters to proceed (matches the client-side validation).
        zip_code = (address_values.get("zip") or "").strip()
        if zip_code and len(zip_code) < 4:
            invalid_fields.add("zip")
            error_messages.append(request.env._("The zip code must have at least 4 characters."))
        return invalid_fields, missing_fields, error_messages

    def _check_billing_address(self, partner_sudo):
        if super()._check_billing_address(partner_sudo):
            return True
        # On an express AR website the derived/optional fields must not block the
        # payment gate (this request has no express_checkout_flow flag set).
        website = request.website
        if website.enable_express_checkout and partner_sudo.country_id.code == "AR":
            mandatory = self._get_mandatory_billing_address_fields(partner_sudo.country_id)
            mandatory = list(mandatory - self._EXPRESS_DERIVED_FIELDS - {"vat"})
            return all(partner_sudo.read(mandatory)[0].values())
        return False

    def _complete_address_values(self, address_values, address_type, use_delivery_as_billing, **kwargs):
        super()._complete_address_values(address_values, address_type, use_delivery_as_billing, **kwargs)
        if getattr(request, "express_checkout_flow", False):
            # AR-only: country is fixed for every partner created in this flow. The
            # tax identity (responsibility, id type) is applied explicitly in
            # _express_apply_tax_identity, so it works whether the partner is newly
            # created or a provisional one being updated.
            address_values["country_id"] = request.env.ref("base.ar").id

    def _express_apply_tax_identity(self, partner_sudo, factura_a):
        """Set country + the AR id type on the (already saved) main partner.

        Factura A: the id type is always CUIT (the buyer entered one); the
        responsibility comes from the form (ARCA-verified or entered by hand) and
        is left untouched. Consumidor Final: derive the responsibility (CF) and the
        id type from the document shape. Kept out of _complete_address_values
        (create-only) so it also applies to the provisional partner reused by the
        CF path. C9: an existing responsibility is never overwritten."""
        env = request.env
        vals = {"country_id": env.ref("base.ar").id}
        if factura_a:
            vals["l10n_latam_identification_type_id"] = env.ref("l10n_ar.it_cuit").id
        elif not partner_sudo.l10n_ar_afip_responsibility_type_id:
            digits = "".join(filter(str.isdigit, partner_sudo.vat or ""))
            id_type = "l10n_ar.it_cuit" if len(digits) == 11 else "l10n_ar.it_dni"
            vals["l10n_latam_identification_type_id"] = env.ref(id_type).id
            vals["l10n_ar_afip_responsibility_type_id"] = env.ref("l10n_ar.res_CF").id
        partner_sudo.sudo().write(vals)

    # ------------------------------------------------------------------
    # Submit
    # ------------------------------------------------------------------
    @route(
        "/shop/express_checkout/submit",
        type="http",
        methods=["POST"],
        auth="public",
        website=True,
        sitemap=False,
    )
    def express_checkout_submit(
        self,
        factura_a=None,
        use_delivery_as_billing=None,
        address_type=None,
        callback=None,
        **form_data,
    ):
        """Single submit for the whole express form.

        ``use_delivery_as_billing`` / ``address_type`` / ``callback`` are captured
        out of ``form_data`` (the inherited address form injects them as hidden
        inputs) and intentionally ignored: we derive the flow from ``factura_a``
        and always advance to the payment step. Leaving them in ``form_data`` would
        collide with the explicit keyword args downstream.

        Consumidor Final: one partner (invoice == shipping == partner_id), tax
        identity derived server-side.

        Factura A: the billing partner is built from the fiscal fields the buyer
        confirmed (ARCA-verified or entered by hand): ``fa_name`` (razón social),
        the CUIT, ``fa_responsibility`` and the fiscal domicile (``fa_*``). A
        separate ``type='delivery'`` child carries the buyer's shipping address.
        """
        order_sudo = request.cart
        if redirection := self._check_cart(order_sudo):
            return json.dumps({"redirectUrl": redirection.location})
        if not self._express_checkout_enabled(order_sudo):
            return json.dumps({"redirectUrl": "/shop/checkout"})

        factura_a = str2bool(factura_a or "false")
        request.express_checkout_flow = True
        request.express_checkout_factura_a = factura_a

        if factura_a:
            feedback = self._express_submit_factura_a(order_sudo, **form_data)
        else:
            _partner, feedback = self._express_create_or_update_main(order_sudo, factura_a=False, **form_data)
        if feedback.get("invalid_fields"):
            return json.dumps(feedback)

        # Safety net: if the buyer never picked a carrier, set the preferred one so
        # the payment step doesn't reject the order for a missing shipping method.
        self._express_ensure_delivery_method(order_sudo)

        # Advance to the extra-info step: when it is not active the native
        # controller forwards straight to /shop/payment, so this honors a
        # configured extra step without us re-implementing its gate. We do not
        # honor a caller-provided redirect target: a forged POST could otherwise
        # turn this into an open redirect.
        return json.dumps({"redirectUrl": "/shop/extra_info"})

    def _express_submit_factura_a(self, order_sudo, **form_data):
        """Build the billing partner from the fiscal (fa_*) fields and the delivery
        child from the shipping address, then wire both to the order."""
        billing_data = self._express_factura_a_billing_data(form_data)
        # Reuse the partner provisioned during delivery rating (order.partner_id on
        # a no-longer-anonymous cart) — or the logged-in partner — as the billing
        # partner, exactly like the CF path. Otherwise a fresh partner would be
        # created as a CHILD of that provisional "Checkout" partner, leaving it
        # orphaned as a spurious parent of both the billing and delivery contacts.
        if order_sudo._is_anonymous_cart():
            partner_sudo = request.env["res.partner"].with_context(show_address=1).sudo().browse()
        else:
            partner_sudo = order_sudo.partner_id
        billing_sudo, feedback = self._create_or_update_address(
            partner_sudo,
            address_type="billing",
            use_delivery_as_billing="false",
            callback="/shop/payment",
            order_sudo=order_sudo,
            **billing_data,
        )
        if feedback.get("invalid_fields"):
            return feedback
        # Country only; the responsibility/id type come from the form (C9 in
        # _express_apply_tax_identity keeps the submitted responsibility).
        self._express_apply_tax_identity(billing_sudo, factura_a=True)
        order_sudo._update_address(billing_sudo.id, {"partner_id", "partner_invoice_id"})
        if order_sudo._is_anonymous_cart():
            order_sudo.message_unsubscribe(order_sudo.website_id.partner_id.ids)
        # Delivery child carries the buyer's shipping address (the contact block).
        return self._express_create_delivery_child(order_sudo, billing_sudo, **form_data)

    def _express_factura_a_billing_data(self, form_data):
        """Map the fiscal (fa_*) form fields to res.partner billing values."""
        env = request.env
        return {
            "name": form_data.get("fa_name") or "",
            "email": form_data.get("email") or "",
            "phone": form_data.get("phone") or "",
            "vat": form_data.get("vat") or "",
            "street": form_data.get("fa_street") or "",
            "city": form_data.get("fa_city") or "",
            "zip": form_data.get("fa_zip") or "",
            "state_id": form_data.get("fa_state_id") or "",
            "country_id": str(env.ref("base.ar").id),
            "l10n_ar_afip_responsibility_type_id": form_data.get("fa_responsibility") or "",
            "l10n_latam_identification_type_id": str(env.ref("l10n_ar.it_cuit").id),
        }

    def _express_ensure_delivery_method(self, order_sudo):
        if not order_sudo._has_deliverable_products() or order_sudo.carrier_id:
            return
        available = order_sudo._get_delivery_methods()
        preferred = order_sudo._get_preferred_delivery_method(available) if available else available
        if preferred:
            order_sudo._set_delivery_method(preferred)

    # ------------------------------------------------------------------
    # Delivery rating — compute + render methods once the address is known
    # ------------------------------------------------------------------
    @route(
        "/shop/express_checkout/delivery_methods",
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def express_checkout_delivery_methods(self, **form):
        """Persist the entered form and return the rendered delivery form so the
        carriers can be rated and selected on the single page."""
        order_sudo = request.cart
        if not order_sudo or not self._express_checkout_enabled(order_sudo):
            return {"delivery_form": ""}
        if not order_sudo._has_deliverable_products():
            return {"delivery_form": ""}
        request.express_checkout_flow = True
        if not self._express_persist_form(order_sudo, form):
            return {"delivery_form": ""}
        values = {
            "delivery_methods": order_sudo._get_delivery_methods(),
            "selected_dm_id": order_sudo.carrier_id.id,
            "order": order_sudo,
        }
        return {"delivery_form": request.env["ir.ui.view"]._render_template("website_sale.delivery_form", values)}

    @route(
        "/shop/express_checkout/save",
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def express_checkout_save(self, **form):
        """Persist the buyer's form on the (provisional) partner without touching
        the delivery methods, so contact/document fields typed after the address
        also survive navigating away and back."""
        order_sudo = request.cart
        if not order_sudo or not self._express_checkout_enabled(order_sudo):
            return {}
        request.express_checkout_flow = True
        self._express_persist_form(order_sudo, form)
        return {}

    def _express_persist_form(self, order_sudo, form):
        """Store the buyer's contact + address (+ CF document) on the cart's
        partner so the express form survives navigating away and back.

        Anonymous cart: provision a partner (with the real name) once the address
        can rate, and set it as the cart's partner (partner_shipping/invoice are
        computed from it); the submit reuses this partner. Guest with that
        provisional partner: rewrite the whole form onto it. Logged-in: only
        refresh the shipping address, never the account's contact data.

        Returns whether the address is complete enough to rate (zip >= 4 digits +
        province)."""
        guest = request.env.user._is_public()
        keys = set(_EXPRESS_CONTACT_FIELDS) | set(_ADDRESS_FIELDS) | {"vat"}
        vals = {key: value for key, value in form.items() if key in keys and value}
        # Only persist a document once it is a complete DNI (7-8) or CUIT (11):
        # partial typing would fail the l10n_ar identification constraint on write.
        doc_digits = "".join(ch for ch in (vals.get("vat") or "") if ch.isdigit())
        if len(doc_digits) not in (7, 8, 11):
            vals.pop("vat", None)
        zip_digits = "".join(ch for ch in (vals.get("zip") or "") if ch.isdigit())
        address_ready = len(zip_digits) >= 4 and bool(vals.get("state_id"))
        vals["country_id"] = str(request.env.ref("base.ar").id)
        address_values, _extra = self._parse_form_data(vals)
        if order_sudo._is_anonymous_cart():
            if not (guest and address_ready):
                return False
            # Provision with the buyer's real name (a neutral fallback only if they
            # completed the address before typing it; the next save fixes it).
            address_values.setdefault("name", request.env._("Cliente"))
            new_partner = self._create_new_address(
                address_values,
                address_type="delivery",
                use_delivery_as_billing=False,
                order_sudo=order_sudo,
            )
            # Don't recompute the pricelist just because the partner changed.
            with request.env.protecting([order_sudo._fields["pricelist_id"]], order_sudo):
                order_sudo.partner_id = new_partner
        elif guest:
            # Our provisional partner: rewrite the whole form so it survives navigation.
            order_sudo.partner_id.sudo().write(address_values)
        else:
            # Logged-in: only refresh the shipping address; never clobber their contact.
            shipping_values = {
                key: value for key, value in address_values.items() if key in set(_ADDRESS_FIELDS) | {"country_id"}
            }
            if shipping_values:
                order_sudo.partner_shipping_id.sudo().write(shipping_values)
        return address_ready

    def _express_create_or_update_main(self, order_sudo, factura_a=False, **form_data):
        """Create/update the main (billing) partner and wire it to the order.

        Reuses the partner provisioned during delivery rating (order.partner_id on
        a no-longer-anonymous cart) so the carrier and address survive; otherwise
        creates a fresh one. The AR tax identity is applied explicitly afterwards
        (so it works on both the create and the update path)."""
        use_delivery_as_billing = not factura_a
        was_anonymous = order_sudo._is_anonymous_cart()
        if was_anonymous:
            partner_sudo = request.env["res.partner"].with_context(show_address=1).sudo().browse()
        else:
            partner_sudo = order_sudo.partner_id

        partner_sudo, feedback = self._create_or_update_address(
            partner_sudo,
            address_type="billing",
            use_delivery_as_billing="true" if use_delivery_as_billing else "false",
            callback="/shop/payment",
            order_sudo=order_sudo,
            **form_data,
        )
        if feedback.get("invalid_fields"):
            return partner_sudo, feedback

        self._express_apply_tax_identity(partner_sudo, factura_a)

        partner_fnames = {"partner_id", "partner_invoice_id"}
        if use_delivery_as_billing:
            partner_fnames.add("partner_shipping_id")
        order_sudo._update_address(partner_sudo.id, partner_fnames)

        if was_anonymous:
            order_sudo.message_unsubscribe(order_sudo.website_id.partner_id.ids)
        return partner_sudo, feedback

    def _express_create_delivery_child(self, order_sudo, main_partner_sudo, **form_data):
        """Create the delivery child (buyer's address) and set it as shipping."""
        delivery_data = {key: value for key, value in form_data.items() if key in _ADDRESS_FIELDS}
        # The delivery address validation requires name/email/phone/country_id too
        # (they are mandatory for a delivery address). Carry the contact data from
        # the main partner and fix the country (AR) so validation passes — the
        # server would otherwise only set the country in _complete_address_values,
        # which runs after validation.
        delivery_data["country_id"] = request.env.ref("base.ar").id
        # The recipient is the contact the buyer entered (not the billing razón
        # social); fall back to the main partner's data.
        delivery_data.setdefault("name", form_data.get("name") or main_partner_sudo.name)
        delivery_data.setdefault("email", form_data.get("email") or main_partner_sudo.email or "")
        delivery_data.setdefault("phone", form_data.get("phone") or main_partner_sudo.phone or "")

        # Reuse the existing delivery child on a re-submit (e.g. the buyer went back
        # and confirmed again) instead of creating a new one each time. The order's
        # shipping partner is that child only when it differs from the billing
        # partner; otherwise (first submit) it still points at the billing/main one,
        # so we create a fresh child.
        existing_child = order_sudo.partner_shipping_id
        target = (
            existing_child.with_context(show_address=1).sudo()
            if existing_child and existing_child != main_partner_sudo
            else request.env["res.partner"].with_context(show_address=1).sudo().browse()
        )
        child_sudo, feedback = self._create_or_update_address(
            target,
            address_type="delivery",
            use_delivery_as_billing="false",
            callback="/shop/payment",
            order_sudo=order_sudo,
            **delivery_data,
        )
        if not feedback.get("invalid_fields"):
            order_sudo._update_address(child_sudo.id, {"partner_shipping_id"})
        return feedback
