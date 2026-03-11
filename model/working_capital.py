class WorkingCapital:
    """Computes AR, AP, Inventory and Net Working Capital from DSO/DPO/DIO."""

    def compute(self, inputs: dict, period: int) -> dict:
        dso = float(inputs.get("dso", 45))
        dpo = float(inputs.get("dpo", 30))
        dio = float(inputs.get("dio", 60))
        revenue = inputs.get("revenue", [0.0] * (period + 1))
        cogs = inputs.get("cogs", [0.0] * (period + 1))

        ar = [0.0]
        ap = [0.0]
        inventory = [0.0]
        nwc = [0.0]
        change_in_wc = [0.0]

        for t in range(1, period + 1):
            a_r = revenue[t] * dso / 365
            a_p = cogs[t] * dpo / 365
            inv = cogs[t] * dio / 365
            nwc_t = a_r + inv - a_p
            delta_wc = nwc_t - nwc[t - 1]

            ar.append(a_r)
            ap.append(a_p)
            inventory.append(inv)
            nwc.append(nwc_t)
            change_in_wc.append(delta_wc)

        return {
            "accounts_receivable": ar,
            "accounts_payable": ap,
            "inventory": inventory,
            "net_working_capital": nwc,
            "change_in_wc": change_in_wc,
        }
