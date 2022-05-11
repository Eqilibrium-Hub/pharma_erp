/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

const { Component, hooks } = owl;
const { useState } = hooks;


export class SwitchDivisionMenu extends Component {
    setup() {
        this.divisionService = useService("division");
        this.currentDivision = this.divisionService.currentDivision;
        this.state = useState({ divisionsToToggle: [] });
    }

    toggleDivision(divisionId) {
        this.state.divisionsToToggle = symmetricalDifference(this.state.divisionsToToggle, [
            divisionId,
        ]);
        browser.clearTimeout(this.toggleTimer);
        this.toggleTimer = browser.setTimeout(() => {
            this.divisionService.setDivisions("toggle", ...this.state.divisionsToToggle);
        }, this.constructor.toggleDelay);
    }

    logIntoDivision(divisionId) {
        browser.clearTimeout(this.toggleTimer);
        this.divisionService.setDivisions("loginto", divisionId);
    }

    get selectedDivisions() {
        return symmetricalDifference(
            this.divisionService.allowedDivisionIds,
            this.state.divisionsToToggle
        );
    }
}
SwitchDivisionMenu.template = "setu_pharma_basic.SwitchDivisionMenu";
SwitchDivisionMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: SwitchDivisionMenu,
    isDisplayed(env) {
        const { availableDivisions } = env.services.division;
        return Object.keys(availableDivisions).length > 1;
    },
};

registry.category("systray").add("SwitchDivisionMenu", systrayItem, { sequence: 1 });
