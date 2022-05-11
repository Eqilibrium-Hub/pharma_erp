/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { symmetricalDifference } from "@web/core/utils/arrays";
import { session } from "@web/session";

function parseDivisionIds(dividsFromHash) {
    const divids = [];
    if (typeof dividsFromHash === "string") {
        divids.push(...dividsFromHash.split(",").map(Number));
    } else if (typeof dividsFromHash === "number") {
        divids.push(dividsFromHash);
    }
    return divids;
}

function computeAllowedDivisionIds(divids) {
    const { user_divisions } = session;
    let allowedDivisionIds = divids || [];
    const availableDivisionsFromSession = user_divisions.allowed_divisions;
    const notReallyAllowedDivisions = allowedDivisionIds.filter(
        (id) => !(id in availableDivisionsFromSession)
    );

    if (!allowedDivisionIds.length || notReallyAllowedDivisions.length) {
        allowedDivisionIds = [user_divisions.current_division];
    }
    return allowedDivisionIds;
}

export const divisionService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {
        let divids;
        if ("divids" in router.current.hash) {
            divids = parseDivisionIds(router.current.hash.divids);
        } else if ("divids" in cookie.current) {
            divids = parseDivisionIds(cookie.current.divids);
        }
        let allowedDivisionIds = computeAllowedDivisionIds(divids);

        const stringDivIds = allowedDivisionIds.join(",");
        router.replaceState({ divids: stringDivIds }, { lock: true });
        cookie.setCookie("divids", stringDivIds);
        user.updateContext({ allowed_division_ids: allowedDivisionIds, division_id: allowedDivisionIds[0] });
        const availableDivisions = session.user_divisions.allowed_divisions;

        return {
            availableDivisions,
            get allowedDivisionIds() {
                return allowedDivisionIds.slice();
            },
            get currentDivision() {
                return availableDivisions[allowedDivisionIds[0]];
            },
            setDivisions(mode, ...divisionIds) {
                let nextDivisionIds;
                if (mode === "toggle") {
                    nextDivisionIds = symmetricalDifference(allowedDivisionIds, divisionIds);
                } else if (mode === "loginto") {
                    const divisionId = divisionIds[0];
                    if (allowedDivisionIds.length === 1) {
                        nextDivisionIds = [divisionId];
                    } else {
                        nextDivisionIds = [
                            divisionId,
                            ...allowedDivisionIds.filter((id) => id !== divisionId),
                        ];
                    }
                }
                nextDivisionIds = nextDivisionIds.length ? nextDivisionIds : [divisionIds[0]];

                router.pushState({ divids: nextDivisionIds }, { lock: true });
                console.log(nextDivisionIds)
                cookie.setCookie("divids", nextDivisionIds);
                browser.setTimeout(() => browser.location.reload());
            },
        };
    },
};

registry.category("services").add("division", divisionService);
