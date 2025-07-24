/** @odoo-module **/

import { registry } from "@web/core/registry";
import { click, insertText } from "@web/../tests/helpers/utils";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import { mount } from "@web/../tests/helpers/utils";
import { GoogleTagManagerUserAdvancedTracking } from "@website_user_tracking/js/website_user_tracking";
import { patchWithCleanup } from "@web/../tests/helpers/utils";
import { session } from "@web/session";
import { expect, test } from "@odoo/hoot";

const publicWidgetRegistry = registry.category("public_widgets");

test("GoogleTagManagerUserAdvancedTracking: _onUserSignup", async () => {
    publicWidgetRegistry.add(
        "GoogleTagManagerUserAdvancedTracking",
        GoogleTagManagerUserAdvancedTracking
    );

    const dataLayer = [];
    patchWithCleanup(window, {
        dataLayer: dataLayer,
    });

    const env = await makeTestEnv({ session });
    const target = document.createElement("div");
    target.classList.add("oe_website_login_container");
    target.innerHTML = `
        <form>
            <input type="email" id="login" name="login" required="required"/>
            <button class="on_user_signup">Sign Up</button>
        </form>
    `;
    document.body.appendChild(target);

    await mount(GoogleTagManagerUserAdvancedTracking, target, { env });

    await insertText("#login", "test@example.com");
    await click("button.on_user_signup");

    expect(dataLayer.length).toBe(1);
    expect(dataLayer[0]).toEqual({
        event: "user_signup",
        user_email: "test@example.com",
    });

    // Cleanup
    target.remove();
    delete publicWidgetRegistry.get("GoogleTagManagerUserAdvancedTracking");
});