class ArohaMaramataka {
    constructor() {
        this.epochNewMoon = new Date('2026-01-18T19:52:00Z').getTime();
        this.synodicMonthDays = 29.5305877057;
    }
    getCurrentPhase(date = new Date()) {
        const diffDays = (date.getTime() - this.epochNewMoon) / (1000 * 60 * 60 * 24);
        const cycleDay = diffDays % this.synodicMonthDays;
        const normalizedDay = cycleDay < 0 ? cycleDay + this.synodicMonthDays : cycleDay;
        let name = "Whiro (New Moon / Rest)", code = "Whiro", energy = "Low / Inward";
        if (normalizedDay >= 1 && normalizedDay < 4) { name = "Tirea / Oho"; code = "Oho"; energy = "Emergent"; }
        else if (normalizedDay >= 4 && normalizedDay < 7) { name = "Ouenuku / Tamatea"; code = "Tamatea"; energy = "Unstable / Transformative"; }
        else if (normalizedDay >= 13 && normalizedDay < 16) { name = "Rākaunui (Full Moon / Expansion)"; code = "Rakaunui"; energy = "Peak / Gold"; }
        else if (normalizedDay >= 22 && normalizedDay < 26) { name = "Tangaroa"; code = "Tangaroa"; energy = "Productive / Tidal"; }
        return { ageDays: parseFloat(normalizedDay.toFixed(2)), name, code, energy, bias: code === 'Rakaunui' ? 0.22 : (code === 'Whiro' ? -0.22 : 0.0) };
    }
}
window.ArohaMaramataka = ArohaMaramataka;
