# app8.py
# Unified app: Home, TCO, Simulation, Agent Efficiency, Models
# Replace previous app7.py with this file.
import streamlit as st
import pandas as pd
import math
import io
import json

st.set_page_config(page_title="Agent Pricing Factory", layout="wide")

# -----------------------
# Defaults (same style as app7)
# -----------------------
DEFAULTS = {
    # TCO defaults
    "tco_one_time_identity": 150000,
    "tco_one_time_vpc": 200000,
    "tco_one_time_observability": 120000,
    "tco_one_time_security": 100000,
    "tco_min_agents": 10,
    "tco_avg_tokens_interaction": 500,
    "tco_interactions_per_agent_month": 1000,
    "tco_token_price_per_1k": 0.046,
    "tco_agent_runtime_cost_per_call": 0.001,
    "tco_recurring_license_monthly": 0.0,
    "tco_vector_db_monthly": 20000.0,
    "tco_embedding_monthly": 15000.0,
    "tco_logging_monthly": 12000.0,
    "tco_api_gateway_monthly": 8000.0,
    "tco_cicd_monthly": 15000.0,
    "tco_maintenance_pct_year": 20,
    "tco_enhancement_pct_year": 10,
    "tco_agent_hours_per_month": 180,
    "tco_human_inloop_pct": 10,
    "tco_human_hourly_rate": 600,
    # per-agent build defaults
    "tco_build_hours_utility": 120,
    "tco_hourly_utility": 1200,
    "tco_build_hours_standard": 240,
    "tco_hourly_standard": 1200,
    "tco_build_hours_professional": 480,
    "tco_hourly_professional": 1400,
    "tco_build_hours_enterprise": 960,
    "tco_hourly_enterprise": 1600,
    "tco_maint_slab_default": 10,
    # Simulation defaults
    "sim_hours": 10000.0,
    "sim_agent_ratio_pct": 0,
    "sim_agent_cm_pct": 45,
    "sim_agent_trio_pct": 5,
    "sim_prod_human": 160,
    "sim_human_blend_cost_hr": 320.0,
    "sim_human_cm_pct": 30,
    "sim_human_trio_pct": 22,
    "sim_human_inloop_pct_global": 0.0,
}

# Ensure session defaults
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def currency(x):
    try:
        return f"SEK {x:,.0f}"
    except Exception:
        return f"SEK {x}"

# Shared list of agent types
AGENT_TYPES = ["Utility", "Standard", "Professional", "Enterprise"]

# -----------------------
# TCO page (same as app7 but minimal repeated code removed)
# -----------------------
def tco_page():
    st.header("TCO — Agent Overall TCO")
    st.markdown("Capture one-time and recurring costs. Values persist in session and can be exported/imported as JSON.")
    st.markdown("---")

    # Part 1
    with st.expander("Part 1 — Foundation (one-time) - Do this calculation outside and feed numbers below ▾", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Identity & Access Setup (one-time SEK)",
                            value=int(st.session_state["tco_one_time_identity"]),
                            key="tco_one_time_identity", step=1000, format="%d")
            st.number_input("VPC / Networking (one-time SEK)",
                            value=int(st.session_state["tco_one_time_vpc"]),
                            key="tco_one_time_vpc", step=1000, format="%d")
        with c2:
            st.number_input("Observability & Logging setup (one-time SEK)",
                            value=int(st.session_state["tco_one_time_observability"]),
                            key="tco_one_time_observability", step=1000, format="%d")
            st.number_input("Initial Security & Compliance (one-time SEK)",
                            value=int(st.session_state["tco_one_time_security"]),
                            key="tco_one_time_security", step=1000, format="%d")
        with c3:
            st.number_input("Minimum Agents (for foundation sizing)",
                            min_value=1, value=int(st.session_state["tco_min_agents"]),
                            key="tco_min_agents", step=1)
            st.caption("Foundation sizing is for the minimum agent bundle (not charged per-agent here).")

        total_foundation = (int(st.session_state["tco_one_time_identity"]) +
                            int(st.session_state["tco_one_time_vpc"]) +
                            int(st.session_state["tco_one_time_observability"]) +
                            int(st.session_state["tco_one_time_security"]))
        st.markdown(f"**Total Foundation One-time:** {currency(total_foundation)}")

    # Part 3: Infra recurring — read tco_min_agents (no duplicate key)
    st.markdown("---")
    with st.expander("Part 3 — Infra / Runtime (monthly for minimum agents) ▾", expanded=True):
        left, right = st.columns(2)
        num_agents = int(st.session_state["tco_min_agents"])
        left.markdown(f"**Number of Agents (for infra calc):** {num_agents:,}")
        with left:
            st.number_input("Avg tokens per interaction", min_value=1,
                            value=int(st.session_state["tco_avg_tokens_interaction"]),
                            key="tco_avg_tokens_interaction", step=1, format="%d")
            st.number_input("Interactions per agent per month", min_value=0,
                            value=int(st.session_state["tco_interactions_per_agent_month"]),
                            key="tco_interactions_per_agent_month", step=1, format="%d")
            st.number_input("Token price per 1k (SEK)", min_value=0.0,
                            value=float(st.session_state["tco_token_price_per_1k"]),
                            key="tco_token_price_per_1k", step=0.000001, format="%.6f")
            st.number_input("Agent runtime cost per call (SEK)", min_value=0.0,
                            value=float(st.session_state["tco_agent_runtime_cost_per_call"]),
                            key="tco_agent_runtime_cost_per_call", step=0.000001, format="%.6f")
            st.number_input("Recurring License cost (SEK/month) — total (for all agents)",
                            min_value=0.0, value=float(st.session_state["tco_recurring_license_monthly"]),
                            key="tco_recurring_license_monthly", step=100.0, format="%.2f")
        with right:
            st.number_input("Vector DB monthly (SEK total)", min_value=0.0,
                            value=float(st.session_state["tco_vector_db_monthly"]), key="tco_vector_db_monthly", step=100.0, format="%.2f")
            st.number_input("Embedding monthly (SEK total)", min_value=0.0,
                            value=float(st.session_state["tco_embedding_monthly"]), key="tco_embedding_monthly", step=100.0, format="%.2f")
            st.number_input("Logging & Monitoring monthly (SEK total)", min_value=0.0,
                            value=float(st.session_state["tco_logging_monthly"]), key="tco_logging_monthly", step=100.0, format="%.2f")
            st.number_input("API Gateway monthly (SEK total)", min_value=0.0,
                            value=float(st.session_state["tco_api_gateway_monthly"]), key="tco_api_gateway_monthly", step=100.0, format="%.2f")
            st.number_input("CI/CD & DevOps monthly (SEK total)", min_value=0.0,
                            value=float(st.session_state["tco_cicd_monthly"]), key="tco_cicd_monthly", step=100.0, format="%.2f")

        # compute infra costs
        token_cost = (num_agents * int(st.session_state["tco_interactions_per_agent_month"]) *
                      int(st.session_state["tco_avg_tokens_interaction"]) *
                      float(st.session_state["tco_token_price_per_1k"]) / 1000.0)
        runtime_call_cost = (num_agents * int(st.session_state["tco_interactions_per_agent_month"]) *
                             float(st.session_state["tco_agent_runtime_cost_per_call"]))
        total_infra_monthly = (token_cost + runtime_call_cost + float(st.session_state["tco_vector_db_monthly"]) +
                               float(st.session_state["tco_embedding_monthly"]) + float(st.session_state["tco_logging_monthly"]) +
                               float(st.session_state["tco_api_gateway_monthly"]) + float(st.session_state["tco_cicd_monthly"]) +
                               float(st.session_state["tco_recurring_license_monthly"]))
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Token cost (SEK/month)", f"{token_cost:,.2f}")
        col2.metric("Total runtime cost (SEK/month)", f"{runtime_call_cost:,.2f}")
        col3.metric("Recurring License (SEK/month)", f"{float(st.session_state['tco_recurring_license_monthly']):,.2f}")
        st.markdown(f"**Total Infra Monthly (all agents):** {currency(total_infra_monthly)}")

    # Part 2: Build costs side-by-side
    st.markdown("---")
    with st.expander("Part 2 — Build & Enhancement Cost Per Agent (one-time) ▾", expanded=False):
        cols = st.columns(4)
        build_costs = {}
        for i, t in enumerate(AGENT_TYPES):
            lower = t.lower()
            with cols[i]:
                st.markdown(f"**{t}**")
                st.number_input("Build effort (hours)", min_value=0,
                                value=int(st.session_state.get(f"tco_build_hours_{lower}", DEFAULTS["tco_build_hours_utility"])),
                                key=f"tco_build_hours_{lower}", step=1, format="%d")
                st.number_input("Hourly rate (SEK/hr)", min_value=0.0,
                                value=float(st.session_state.get(f"tco_hourly_{lower}", DEFAULTS["tco_hourly_utility"])),
                                key=f"tco_hourly_{lower}", step=50.0, format="%.2f")
                hours = int(st.session_state[f"tco_build_hours_{lower}"])
                rate = float(st.session_state[f"tco_hourly_{lower}"])
                bc = hours * rate
                st.metric("Build cost (one-time SEK)", f"{int(bc):,}")
                build_costs[t] = bc

    # Part 4: Maintenance & enhancement monthly
    st.markdown("---")
    with st.expander("Part 4 — Maintenance & Enhancement per Agent (monthly) ▾", expanded=False):
        cols = st.columns(4)
        maint_monthly = {}
        enh_monthly = {}
        for i, t in enumerate(AGENT_TYPES):
            lower = t.lower()
            with cols[i]:
                st.markdown(f"**{t}**")
                st.number_input("Maintenance % of build (per year)", min_value=0, max_value=100,
                                value=int(st.session_state.get(f"tco_maint_pct_{lower}", DEFAULTS["tco_maintenance_pct_year"])),
                                key=f"tco_maint_pct_{lower}", step=1, format="%d")
                st.number_input("Enhancement % of build (per year)", min_value=0, max_value=100,
                                value=int(st.session_state.get(f"tco_enh_pct_{lower}", DEFAULTS["tco_enhancement_pct_year"])),
                                key=f"tco_enh_pct_{lower}", step=1, format="%d")
                st.number_input("Maint monthly baseline (per slab)",
                                min_value=0, value=int(st.session_state.get(f"tco_maint_per_slab_{lower}", 0)),
                                key=f"tco_maint_per_slab_{lower}", step=100, format="%d")
                st.number_input("Maint slab size (agents)", min_value=1,
                                value=int(st.session_state.get(f"tco_maint_slab_{lower}", DEFAULTS["tco_maint_slab_default"])),
                                key=f"tco_maint_slab_{lower}", step=1, format="%d")
                build_cost = build_costs.get(t, 0)
                maint_m = (build_cost * float(st.session_state[f"tco_maint_pct_{lower}"]) / 100.0) / 12.0
                enh_m = (build_cost * float(st.session_state[f"tco_enh_pct_{lower}"]) / 100.0) / 12.0
                st.metric("Maintenance / month (SEK)", f"{maint_m:,.2f}")
                st.metric("Enhancement / month (SEK)", f"{enh_m:,.2f}")
                maint_monthly[t] = maint_m
                enh_monthly[t] = enh_m

    # Part 5: Human-in-loop per agent
    st.markdown("---")
    with st.expander("Part 5 — Human-in-loop (per agent/month) ▾", expanded=False):
        cols = st.columns(4)
        human_monthly = {}
        for i, t in enumerate(AGENT_TYPES):
            lower = t.lower()
            with cols[i]:
                st.markdown(f"**{t}**")
                st.number_input("Agent hours delivered (hrs/month)", min_value=1,
                                value=int(st.session_state.get(f"tco_agent_hours_{lower}", DEFAULTS["tco_agent_hours_per_month"])),
                                key=f"tco_agent_hours_{lower}", step=1, format="%d")
                st.number_input("Human-in-loop % (per agent)", min_value=0, max_value=100,
                                value=int(st.session_state.get(f"tco_human_pct_{lower}", DEFAULTS["tco_human_inloop_pct"])),
                                key=f"tco_human_pct_{lower}", step=1, format="%d")
                st.number_input("Human hourly rate (SEK/hr)",
                                min_value=0.0, value=float(st.session_state.get(f"tco_human_rate_{lower}", DEFAULTS["tco_human_hourly_rate"])),
                                key=f"tco_human_rate_{lower}", step=10.0, format="%.2f")
                agent_hours = int(st.session_state[f"tco_agent_hours_{lower}"])
                human_pct = int(st.session_state[f"tco_human_pct_{lower}"])
                human_rate = float(st.session_state[f"tco_human_rate_{lower}"])
                human_hours = agent_hours * human_pct / 100.0
                human_cost = human_hours * human_rate
                st.metric("Human hours / agent / month", f"{human_hours:,.2f}")
                st.metric("Human cost / agent / month (SEK)", f"{human_cost:,.2f}")
                human_monthly[t] = human_cost

    # Part 6: One-time licenses
    st.markdown("---")
    with st.expander("Part 6 — One-time License Cost (CapEx) ▾", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("RPA License (one-time SEK)", min_value=0,
                            value=int(st.session_state.get("tco_one_time_rpa_license", 0)), key="tco_one_time_rpa_license", step=1000, format="%d")
            st.number_input("Orchestration / Orchestrator License (one-time SEK)", min_value=0,
                            value=int(st.session_state.get("tco_one_time_orch_license", 0)), key="tco_one_time_orch_license", step=1000, format="%d")
        with c2:
            st.number_input("Analytics / BI License (one-time SEK)", min_value=0,
                            value=int(st.session_state.get("tco_one_time_analytics_license", 0)), key="tco_one_time_analytics_license", step=1000, format="%d")
            st.number_input("Other One-time Licenses (SEK)", min_value=0, value=int(st.session_state.get("tco_one_time_other_license", 0)),
                            key="tco_one_time_other_license", step=1000, format="%d")

        total_one_time_licenses = (int(st.session_state.get("tco_one_time_rpa_license", 0)) +
                                   int(st.session_state.get("tco_one_time_orch_license", 0)) +
                                   int(st.session_state.get("tco_one_time_analytics_license", 0)) +
                                   int(st.session_state.get("tco_one_time_other_license", 0)))
        st.markdown(f"**Total One-time Licenses (CapEx):** {currency(total_one_time_licenses)}")

    # Snapshot / Save-Load JSON
    st.markdown("---")
    st.subheader("TCO Snapshot & Save / Load")
    tco_keys = {k: v for k, v in st.session_state.items() if k.startswith("tco_")}
    try:
        prof_json = json.dumps(tco_keys, indent=2)
        st.download_button("Download TCO JSON", data=prof_json.encode("utf-8"), file_name="tco_profile.json", mime="application/json")
    except Exception:
        st.info("Unable to prepare TCO JSON export.")
    uploaded = st.file_uploader("Upload TCO JSON to load (will overwrite tco_ session keys)", type=["json"])
    if uploaded:
        try:
            loaded = json.load(uploaded)
            for k, v in loaded.items():
                if k.startswith("tco_"):
                    st.session_state[k] = v
            st.success("TCO profile loaded into session. Page will reflect new values.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to load JSON: {e}")

# -----------------------
# Simulation page (keep app7 logic)
# -----------------------
def simulation_page():
    st.header("Simulation — Agent vs Human")
    st.markdown("Model total work-hours (annual), agent counts, human in-loop and see simplified financials. Reads TCO where relevant.")
    # For brevity, reuse app7 simulation code (same as in previous version)
    # We'll call the same function body as app7's simulation_page
    # (To keep this file compact I will re-use the earlier simulation_page implementation)
    # For production you might refactor to avoid duplication.

    # --- Project size
    with st.expander("1) Project Size", expanded=True):
        total_hours = st.number_input("Total work-hours to model (annual)", min_value=1.0,
                                      value=float(st.session_state["sim_hours"]), step=1.0, key="sim_hours", format="%.0f")
        agent_ratio_pct = st.slider("Agent Ratio (target % of total work handled by Agents)", 0, 100,
                                    int(st.session_state["sim_agent_ratio_pct"]), key="sim_agent_ratio_pct")
        agent_hr_max = int(total_hours * (agent_ratio_pct / 100.0))
        human_hr_max = int(total_hours - agent_hr_max)
        st.markdown(f"- Agent Hr target (annual): **{agent_hr_max:,}**")
        st.markdown(f"- Human Hr target (annual): **{human_hr_max:,}**")

    st.markdown("---")

    # --- Solutioned Agents (simple)
    with st.expander("2) Solutioned Agents (configure counts & productivity)", expanded=True):
        st.write("Agent settings come from the TCO page. Change counts & productive hours here.")
        # sliders for global Agent CM and Trio
        sim_agent_cm_pct = st.slider("Agent default CM % (global)", 0, 100, int(st.session_state["sim_agent_cm_pct"]), key="sim_agent_cm_pct")
        sim_agent_trio_pct = st.slider("Agent default Trio % (global)", 0, 100, int(st.session_state["sim_agent_trio_pct"]), key="sim_agent_trio_pct")

        # rows for agents
        AGENTS = []
        agents_rows = []
        for t in AGENT_TYPES:
            lower = t.lower()
            build_hours = float(st.session_state.get(f"tco_build_hours_{lower}", DEFAULTS["tco_build_hours_utility"]))
            hourly_rate = float(st.session_state.get(f"tco_hourly_{lower}", DEFAULTS["tco_hourly_utility"]))
            build_one_time = int(build_hours * hourly_rate)
            maint_per_slab = int(st.session_state.get(f"tco_maint_per_slab_{lower}", 0))
            maint_slab_size = int(st.session_state.get(f"tco_maint_slab_{lower}", DEFAULTS["tco_maint_slab_default"]))
            enh_pct = float(st.session_state.get(f"tco_enh_pct_{lower}", DEFAULTS["tco_enhancement_pct_year"]))
            default_prodhrs = int(st.session_state.get(f"tco_agent_hours_{lower}", DEFAULTS["tco_agent_hours_per_month"]))

            cols = st.columns([2,1,1,1,1,1])
            cols[0].write(f"**{t}**")
            cols[1].write(f"Build: {build_one_time:,}")

            prod_key = f"sim_agent_prodhrs_{lower}"
            if prod_key not in st.session_state:
                st.session_state[prod_key] = default_prodhrs
            prod_hrs = cols[3].number_input(f"ProdHrs/mo {t}", min_value=1, value=int(st.session_state[prod_key]), key=prod_key, step=1, format="%d")

            count_key = f"sim_count_{lower}"
            if count_key not in st.session_state:
                st.session_state[count_key] = 0
            cnt = cols[4].number_input(f"Count {t}", min_value=0, value=int(st.session_state[count_key]), step=1, key=count_key, format="%d")

            # calculations
            total_build = build_one_time * cnt
            enh_yearly_total = int((enh_pct / 100.0) * build_one_time * cnt)
            dev_amort_month = (build_one_time / 12.0)
            if cnt == 0:
                maint_total_month = 0
            else:
                slabs = math.ceil(cnt / max(1, maint_slab_size))
                maint_total_month = int(maint_per_slab * slabs)

            monthly_enh_component = enh_yearly_total / 12.0
            monthly_base_cost = dev_amort_month + maint_total_month + monthly_enh_component
            if cnt == 0:
                blended_price_month = 0
                price_per_hr = 0
                cm_display = 0
                trio_display = 0
            else:
                blended_price_month = int(round(monthly_base_cost * (1 + (sim_agent_cm_pct - sim_agent_trio_pct) / 100.0)))
                price_per_hr = int(blended_price_month / prod_hrs) if prod_hrs > 0 else 0
                cm_display = sim_agent_cm_pct
                trio_display = sim_agent_trio_pct

            capacity_ann = int(prod_hrs * 12 * cnt)
            cols[2].write(f"Maint/mo: {maint_total_month:,}")
            cols[5].write(f"Price/mo: {blended_price_month:,}")

            AGENTS.append({
                "type": t, "count": int(cnt), "prod_hrs_per_month": int(prod_hrs),
                "capacity_ann": capacity_ann, "build_one_time": build_one_time,
                "maint_monthly": maint_total_month, "enh_yearly_total": enh_yearly_total,
                "dev_amort_month": dev_amort_month, "blended_price_month": blended_price_month,
                "price_per_hr": price_per_hr, "cm_pct": cm_display, "trio_pct": trio_display,
            })

            agents_rows.append({
                "AgentType": t, "Count": int(cnt), "Prod_Hrs/Mo": int(prod_hrs),
                "CapacityAnn": capacity_ann, "BuildOneTime": build_one_time, "Maint/mo": int(maint_total_month),
                "EnhYearly": int(enh_yearly_total), "DevAmort/mo": int(dev_amort_month), "Price/mo": int(blended_price_month),
                "Price/hr": int(price_per_hr), "CM%": int(cm_display) if cnt>0 else 0, "Trio%": int(trio_display) if cnt>0 else 0,
            })

    st.markdown("---")

    # --- Human solution
    with st.expander("3) Human Solution (configure)", expanded=True):
        human_prod_hours_per_month = st.number_input("Human productive hrs/month", min_value=1,
                                                     value=int(st.session_state["sim_prod_human"]),
                                                     key="sim_prod_human", step=1, format="%d")
        human_blend_cost_hr = st.number_input("Human blend cost / hr (SEK)", min_value=0.0,
                                             value=float(st.session_state["sim_human_blend_cost_hr"]), step=1.0, key="sim_human_blend_cost_hr",
                                             format="%.2f")
        human_cm_pct = st.number_input("Human CM % (pricing)", min_value=0, max_value=100,
                                       value=int(st.session_state["sim_human_cm_pct"]), key="sim_human_cm_pct",
                                       step=1, format="%d")
        human_trio_pct = st.number_input("Human Trio % (pricing)", min_value=0, max_value=100,
                                        value=int(st.session_state["sim_human_trio_pct"]), key="sim_human_trio_pct",
                                        step=1, format="%d")
        human_inloop_pct_percent = st.slider("Human in loop to cover from % of Agent hr (percent)",
                                             0, 100, int(round(st.session_state.get("sim_human_inloop_pct_global", 0.0)*100)),
                                             key="sim_human_inloop_pct_percent")
        human_in_loop_pct_global = human_inloop_pct_percent / 100.0
        st.session_state["sim_human_inloop_pct_global"] = human_in_loop_pct_global

    # Live calculations and display summarized results (same approach as app7)
    total_agent_capacity_ann = sum(a["capacity_ann"] for a in AGENTS)
    agent_hours_ann_delivered = int(min(total_agent_capacity_ann, agent_hr_max))
    human_inloop_hours = int(round(agent_hours_ann_delivered * human_in_loop_pct_global))
    residual_hours_ann = max(0, int(total_hours - agent_hours_ann_delivered))
    human_hours_ann = residual_hours_ann + human_inloop_hours
    human_annual_capacity_per_person = int(human_prod_hours_per_month * 12)
    human_headcount_required = int(math.ceil(human_hours_ann / human_annual_capacity_per_person)) if human_annual_capacity_per_person > 0 else 0

    agent_revenue_ann = sum(a["blended_price_month"] * 12 * a["count"] for a in AGENTS)
    agent_dev_amort_ann = sum(int(a["dev_amort_month"] * 12) * a["count"] for a in AGENTS)
    agent_maint_ann = sum(int(a["maint_monthly"] * 12) for a in AGENTS)
    agent_enh_ann = sum(int(a["enh_yearly_total"]) for a in AGENTS)
    agent_direct_costs_ann = agent_dev_amort_ann + agent_maint_ann + agent_enh_ann

    human_cost_direct_ann = human_blend_cost_hr * human_hours_ann
    if human_hours_ann == 0:
        human_price_hr = 0
        human_revenue_ann = 0
    else:
        human_price_hr = human_blend_cost_hr * (1 + max(0.0, (human_cm_pct - human_trio_pct)) / 100.0)
        human_revenue_ann = human_price_hr * human_hours_ann

    total_revenue_ann = agent_revenue_ann + human_revenue_ann
    total_direct_costs_ann = agent_direct_costs_ann + human_cost_direct_ann
    total_contribution_financial = total_revenue_ann - total_direct_costs_ann
    total_trio_financial = (agent_revenue_ann * (sim_agent_trio_pct / 100.0)) + (human_revenue_ann * (human_trio_pct / 100.0))
    total_gop_financial = total_contribution_financial - total_trio_financial

    # Final Team structure
    st.subheader("Final Team Structure")
    if agents_rows:
        df_agents = pd.DataFrame(agents_rows)
        st.table(df_agents)
    st.markdown(f"- Agent total capacity (ann): **{int(total_agent_capacity_ann):,} hrs**")
    st.markdown(f"- Agent hours delivered (ann): **{int(agent_hours_ann_delivered):,} hrs**")
    st.markdown(f"- Human total hrs (ann): **{int(human_hours_ann):,}** (residual {residual_hours_ann:,} + in-loop {human_inloop_hours:,})")
    st.markdown(f"- Human headcount required: **{human_headcount_required:,}**")
    if total_agent_capacity_ann < agent_hr_max:
        st.warning("Agent capacity is LESS than the target Agent Hr. Increase agent counts or their productivity, or reduce target ratio.")
    if total_agent_capacity_ann > agent_hr_max:
        st.info("Agent capacity exceeds target (you have spare capacity).")

    # Financials simplified (weighted combined CM & Trio by revenue)
    st.subheader("Financials — Simplified (annual SEK)")
    agent_headcount = sum(a["count"] for a in AGENTS)
    agent_total_hr = total_agent_capacity_ann
    agent_cost_hr = (agent_direct_costs_ann / agent_total_hr) if agent_total_hr > 0 else 0.0
    agent_cost_month = agent_direct_costs_ann / 12.0
    agent_cm_display = sim_agent_cm_pct if agent_headcount > 0 else 0
    agent_trio_display = sim_agent_trio_pct if agent_headcount > 0 else 0
    agent_gop_display = agent_cm_display - agent_trio_display if agent_headcount > 0 else 0

    human_cost_hr = human_blend_cost_hr
    human_cost_month = human_cost_direct_ann / 12.0 if human_cost_direct_ann > 0 else 0.0
    human_cm_display = human_cm_pct if human_hours_ann > 0 else 0
    human_trio_display = human_trio_pct if human_hours_ann > 0 else 0
    human_gop_display = human_cm_display - human_trio_display if human_hours_ann > 0 else 0

    # Combined weighted by revenue
    if total_revenue_ann > 0:
        combined_cm_weighted = 0.0
        combined_trio_weighted = 0.0
        if agent_revenue_ann > 0:
            combined_cm_weighted += agent_revenue_ann * (agent_cm_display / 100.0)
            combined_trio_weighted += agent_revenue_ann * (agent_trio_display / 100.0)
        if human_revenue_ann > 0:
            combined_cm_weighted += human_revenue_ann * (human_cm_display / 100.0)
            combined_trio_weighted += human_revenue_ann * (human_trio_display / 100.0)
        combined_cm_display_pct = (combined_cm_weighted / total_revenue_ann) * 100.0
        combined_trio_display_pct = (combined_trio_weighted / total_revenue_ann) * 100.0
    else:
        tot_hr = agent_total_hr + human_hours_ann
        if tot_hr > 0:
            combined_cm_display_pct = ((agent_total_hr * agent_cm_display) + (human_hours_ann * human_cm_display)) / tot_hr
            combined_trio_display_pct = ((agent_total_hr * agent_trio_display) + (human_hours_ann * human_trio_display)) / tot_hr
        else:
            combined_cm_display_pct = 0.0
            combined_trio_display_pct = 0.0
    combined_gop_display_pct = combined_cm_display_pct - combined_trio_display_pct

    rows = [
        {"Category": "Agent", "FTE/FTA Count": agent_headcount, "Total Hr (ann)": agent_total_hr,
         "Cost/hr (SEK)": f"{agent_cost_hr:,.2f}", "Cost/mo (SEK)": f"{agent_cost_month:,.2f}",
         "CM % (pricing)": f"{agent_cm_display:.2f}%", "Trio %": f"{agent_trio_display:.2f}%", "GOP % (pricing)": f"{agent_gop_display:.2f}%"},
        {"Category": "Human", "FTE/FTA Count": human_headcount_required, "Total Hr (ann)": human_hours_ann,
         "Cost/hr (SEK)": f"{human_cost_hr:,.2f}", "Cost/mo (SEK)": f"{human_cost_month:,.2f}",
         "CM % (pricing)": f"{human_cm_display:.2f}%", "Trio %": f"{human_trio_display:.2f}%", "GOP % (pricing)": f"{human_gop_display:.2f}%"},
        {"Category": "Combined", "FTE/FTA Count": agent_headcount + human_headcount_required, "Total Hr (ann)": agent_total_hr + human_hours_ann,
         "Cost/hr (SEK)": f"{(total_direct_costs_ann / (agent_total_hr + human_hours_ann) if (agent_total_hr + human_hours_ann) > 0 else 0):,.2f}",
         "Cost/mo (SEK)": f"{(total_direct_costs_ann / 12.0):,.2f}", "CM % (pricing)": f"{combined_cm_display_pct:.2f}%",
         "Trio %": f"{combined_trio_display_pct:.2f}%", "GOP % (pricing)": f"{combined_gop_display_pct:.2f}%"},
    ]
    fin_df = pd.DataFrame(rows).set_index("Category")
    st.dataframe(fin_df, use_container_width=True)

    true_cm_pct = (total_contribution_financial / total_revenue_ann * 100.0) if total_revenue_ann > 0 else 0.0
    true_gop_pct = (total_gop_financial / total_revenue_ann * 100.0) if total_revenue_ann > 0 else 0.0
    c1, c2 = st.columns(2)
    c1.metric("True combined financial CM %", f"{true_cm_pct:.2f}%", help=f"Contribution / revenue = {int(total_contribution_financial):,} / {int(total_revenue_ann) if total_revenue_ann else 0}")
    c2.metric("True combined financial GOP %", f"{true_gop_pct:.2f}%", help=f"GOP / revenue = {int(total_gop_financial):,} / {int(total_revenue_ann) if total_revenue_ann else 0}")

    # Exports
    st.markdown("---")
    st.subheader("Export results")
    csv_df = pd.DataFrame(agents_rows + [{"AgentType": "Human", "Count": human_headcount_required, "CapacityAnn": int(human_hours_ann)}])
    st.download_button("Download team CSV", csv_df.to_csv(index=False).encode("utf-8"), file_name="team_structure.csv", mime="text/csv")
    try:
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            pd.DataFrame(agents_rows).to_excel(writer, sheet_name="agents", index=False)
            pd.DataFrame(rows).to_excel(writer, sheet_name="financials", index=False)
        out.seek(0)
        st.download_button("Download results XLSX", out.read(), file_name="simulation_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        st.info("Install openpyxl to enable .xlsx export.")

# -----------------------
# Agent Efficiency page (new)
# -----------------------
def agent_efficiency_page():
    st.header("Agent Efficiency — Simulator & Pricing Models")
    st.markdown("Compare operation modes (Manual, Assistive, Semi-autonomous, Autonomous). This simulator computes hourly capacity and % savings vs Manual, plus a quick pricing view.")

    # Reference table (default values inspired by your earlier table)
    modes = [
        {"Mode": "Manual (today)", "AvgTimeMin": 55.0},
        {"Mode": "Assistive (stage 1)", "AvgTimeMin": 25.0},  # representative
        {"Mode": "Semi-Autonomous (stage 2)", "AvgTimeMin": 12.5},
        {"Mode": "Autonomous (target)", "AvgTimeMin": 4.0},
    ]

    st.markdown("### Quick reference (avg time per case)")
    df_ref = pd.DataFrame(modes)
    df_ref["Time_hours"] = df_ref["AvgTimeMin"] / 60.0
    st.table(df_ref[["Mode", "AvgTimeMin", "Time_hours"]].rename(columns={"AvgTimeMin": "Avg time/case (min)", "Time_hours": "Time/case (hrs)"}))

    st.markdown("---")
    with st.expander("Simulator inputs", expanded=True):
        cases_per_ann = st.number_input("Cases to model (annual)", min_value=1, value=1000, step=1, key="ae_cases")
        hours_per_fte_ann = st.number_input("FTE productive hours / year", min_value=1, value=160*12, step=1, key="ae_fte_hours")
        human_cost_hr = st.number_input("Human blended cost / hr (SEK)", min_value=0.0,
                                        value=float(st.session_state.get("sim_human_blend_cost_hr", 320.0)),
                                        step=1.0, key="ae_human_cost_hr")
        show_detailed = st.checkbox("Show detailed per-mode breakdown", value=True, key="ae_show_detailed")

    # Compute per-mode metrics (use editable session keys for times)
    # Initialize session defaults for per-mode editable times (only if missing)
    for m in modes:
        key = f"ae_time_{m['Mode']}"
        if key not in st.session_state:
            st.session_state[key] = m["AvgTimeMin"]

    # Build rows
    manual_time = st.session_state[f"ae_time_{modes[0]['Mode']}"]  # Manual entry from session
    manual_hours_per_case = manual_time / 60.0
    manual_total_hours = manual_hours_per_case * cases_per_ann

    rows = []
    for m in modes:
        key = f"ae_time_{m['Mode']}"
        # Widget: put each number_input into its column, but DO NOT assign back to session_state manually
        # We ensure default exists above so widget uses that initial value
        # We'll show the editable widgets below if show_detailed == True
        time_min = float(st.session_state.get(key, m["AvgTimeMin"]))
        time_hr = time_min / 60.0
        total_hours = time_hr * cases_per_ann
        fte_req = total_hours / hours_per_fte_ann
        fte_req_rounded = math.ceil(fte_req)
        cost = total_hours * human_cost_hr
        manual_total_hours_local = manual_total_hours
        savings_vs_manual_pct = ((manual_total_hours_local - total_hours) / manual_total_hours_local * 100.0) if manual_total_hours_local > 0 else 0.0

        rows.append({
            "Mode": m["Mode"],
            "Avg time/case (min)": time_min,
            "Time/case (hrs)": round(time_hr, 4),
            "Total hrs (ann)": int(total_hours),
            "FTE req (ann)": fte_req_rounded,
            "Cost (ann, SEK)": int(cost),
            "% savings vs Manual (hrs)": f"{savings_vs_manual_pct:.1f}%"
        })

    res_df = pd.DataFrame(rows).set_index("Mode")
    st.markdown("### Quick summary")
    st.table(res_df)

    # Detailed editable times (create widgets once; they write to session_state automatically)
    if show_detailed:
        st.markdown("---")
        st.markdown("### Per-mode editable times (minutes)")
        cols = st.columns(len(modes))
        for i, m in enumerate(modes):
            key = f"ae_time_{m['Mode']}"
            # ensure we only call the widget once; we do NOT reassign st.session_state[key] ourselves
            cols[i].number_input(label=m["Mode"], min_value=0.1,
                                 value=float(st.session_state[key]),
                                 key=key, step=0.1, format="%.1f")

    # Pricing quick view (derive approximate per-agent monthly cost from TCO heuristics)
    st.markdown("---")
    st.subheader("Quick pricing view (per-mode)")
    # derive approximate agent monthly cost from TCO averages (simple heuristic)
    avg_build = 0.0
    avg_maint_pct = 0.0
    cnt = 0
    for t in AGENT_TYPES:
        bh = float(st.session_state.get(f"tco_build_hours_{t.lower()}", DEFAULTS["tco_build_hours_utility"]))
        hr = float(st.session_state.get(f"tco_hourly_{t.lower()}", DEFAULTS["tco_hourly_utility"]))
        avg_build += bh * hr
        avg_maint_pct += float(st.session_state.get(f"tco_maint_pct_{t.lower()}", DEFAULTS["tco_maintenance_pct_year"]))
        cnt += 1
    if cnt:
        avg_build /= cnt
        avg_maint_pct /= cnt
    amort_month = avg_build / 36.0
    maint_month = (avg_maint_pct / 100.0) * avg_build / 12.0
    infra_month_per_agent = float(st.session_state.get("tco_recurring_license_monthly", 0.0)) / max(1, int(st.session_state.get("tco_min_agents", 1)))
    approx_capgemini_cost_per_agent_month = amort_month + maint_month + infra_month_per_agent

    st.markdown(f"Approx Capgemini cost per agent (monthly, heuristic): **{currency(approx_capgemini_cost_per_agent_month)}**")

    margin = st.slider("Capgemini margin % to apply on cost (for pricing)", 0, 100, 40, key="ae_margin_pct")
    pricing_rows = []
    for m in modes:
        price_month = approx_capgemini_cost_per_agent_month * (1 + margin / 100.0)
        pricing_rows.append({"Mode": m["Mode"], "Price per agent / month (SEK)": int(price_month)})
    pr_df = pd.DataFrame(pricing_rows).set_index("Mode")
    st.table(pr_df)


# -----------------------
# Models page (Model 1,2,4 on same page)
# -----------------------
def models_page():
    st.header("Commercial Models — FTE Pricing Variants")
    st.markdown("Three practical commercial models. Each section is a self-contained miniature calculator mapped to TCO where needed.")

    # Model 1 — FTE Optimization (Replace FTEs)
    
    with st.expander("Model 1 — FTE Optimization (Replace FTEs)", expanded=True):
        st.markdown("Model 1 calculates agents required to replace a number of current FTEs and shows financials.")
        # inputs: current FTEs, human cost, agent price (from TCO proxies)
        cur_ftes = st.number_input("Current ADM FTEs", min_value=0, value=10, step=1, key="m1_cur_ftes")
        human_cost_hr = st.number_input("Human blended cost / hr (SEK)", min_value=0.0,
                                        value=float(st.session_state.get("sim_human_blend_cost_hr", 320.0)), step=1.0, key="m1_human_cost_hr")
        human_prod_hrs_mo = st.number_input("Human productive hrs / month", min_value=1, value=160, step=1, key="m1_human_prod_hrs")
        # derive agent monthly price from TCO heuristic (re-use agent_efficiency heuristic)
        # reuse approx from agent_efficiency_page logic
        avg_build = 0
        for t in AGENT_TYPES:
            avg_build += float(st.session_state.get(f"tco_build_hours_{t.lower()}", DEFAULTS["tco_build_hours_utility"])) * float(st.session_state.get(f"tco_hourly_{t.lower()}", DEFAULTS["tco_hourly_utility"]))
        avg_build = avg_build / max(1, len(AGENT_TYPES))
        amort_month = avg_build / 36.0
        maint_month = (sum(float(st.session_state.get(f"tco_maint_pct_{t.lower()}", DEFAULTS["tco_maintenance_pct_year"])) for t in AGENT_TYPES) / len(AGENT_TYPES)) * avg_build / 1200.0
        infra_month_per_agent = float(st.session_state.get("tco_recurring_license_monthly", 0.0)) / max(1, int(st.session_state.get("tco_min_agents", 1)))
        base_agent_cost_month = amort_month + maint_month + infra_month_per_agent
        agent_margin_pct = st.slider("Agent margin % (to Telia)", 0, 100, 30, key="m1_agent_margin")
        agent_price_month = base_agent_cost_month * (1 + agent_margin_pct / 100.0)
        # compute replacement
        human_monthly_hours_per_fte = human_prod_hrs_mo
        human_total_month_hours = cur_ftes * human_monthly_hours_per_fte
        # assume agent productive hours per month default
        agent_prod_hrs = st.number_input("Agent productive hrs / month (per agent)", min_value=1, value=180, step=1, key="m1_agent_prod_hrs")
        agents_needed = math.ceil(human_total_month_hours / agent_prod_hrs) if agent_prod_hrs > 0 else 0
        total_agent_price_month = agents_needed * agent_price_month
        # current human cost/month
        human_cost_month = cur_ftes * human_monthly_hours_per_fte * human_cost_hr
        savings_month = human_cost_month - total_agent_price_month
        st.markdown(f"- Agents needed to replace {cur_ftes} FTEs: **{agents_needed}**")
        st.markdown(f"- Current human cost / month: **{currency(human_cost_month)}**")
        st.markdown(f"- Agent cost / month (Telia price): **{currency(total_agent_price_month)}**")
        st.markdown(f"- Net monthly savings (Human - Agent): **{currency(savings_month)}**")
        if savings_month < 0:
            st.warning("Net monthly savings is negative (agents more expensive than humans). Re-check inputs or margin.")

    # Model 2 — FTE Uplift (Increase Productivity)
    with st.expander("Model 2 — FTE Uplift (Increase Productivity)", expanded=False):
        st.markdown("Model 2 shows uplift (productivity improvement) and how many FTE-equivalents it buys.")
        base_cases_ann = st.number_input("Base cases per year (current)", min_value=1, value=10000, step=1, key="m2_cases")
        base_time_per_case_min = st.number_input("Current avg time per case (min)", min_value=0.1, value=55.0, step=0.1, key="m2_base_time")
        new_time_per_case_min = st.number_input("New avg time per case with agent (min)", min_value=0.1, value=25.0, step=0.1, key="m2_new_time")
        hours_saved_ann = (base_time_per_case_min - new_time_per_case_min) / 60.0 * base_cases_ann
        fte_equiv = hours_saved_ann / (160*12)
        st.markdown(f"- Annual hours saved: **{int(hours_saved_ann):,} hrs**")
        st.markdown(f"- Equivalent FTEs freed (ann): **{fte_equiv:.2f} FTEs**")
        # financials using human blended cost
        human_cost_hr = st.number_input("Human blended cost / hr (SEK)", min_value=0.0,
                                        value=float(st.session_state.get("sim_human_blend_cost_hr", 320.0)), step=1.0, key="m2_human_cost_hr")
        ann_saving_sek = hours_saved_ann * human_cost_hr
        st.markdown(f"- Annual saving (pure labour cost): **{currency(ann_saving_sek)}**")

    # Model 4 — Hybrid FTE-Elastic (Dual-mode)
    with st.expander("Model 4 — Hybrid FTE-Elastic (Dual-mode)", expanded=False):
        st.markdown("Model 4 allows part of workload to be handled by agents and burst-managed by humans.")
        total_work_hours = st.number_input("Total work-hours (annual)", min_value=1.0, value=10000.0, step=1.0, key="m4_total_hours")
        agent_coverage_pct = st.slider("Agent coverage % of workload", 0, 100, 40, key="m4_agent_cov")
        burst_pct = st.slider("Burst capacity % (humans cover extra % above steady load)", 0, 100, 20, key="m4_burst_pct")
        # compute hours
        agent_hours = total_work_hours * (agent_coverage_pct / 100.0)
        human_hours = total_work_hours - agent_hours
        # burst headroom calculation
        steady_human_hours = human_hours * (1 - burst_pct/100.0)
        burst_hours = human_hours - steady_human_hours
        st.markdown(f"- Agent hours (ann): **{int(agent_hours):,}**")
        st.markdown(f"- Human steady hours (ann): **{int(steady_human_hours):,}**, burst hours (ann): **{int(burst_hours):,}**")
        # simple cost comparison
        human_cost_hr = st.number_input("Human cost / hr (SEK)", min_value=0.0, value=320.0, step=1.0, key="m4_human_cost_hr")
        agent_price_month_override = st.number_input("Agent price/mo (Telia) override (SEK) — 0 to use TCO heuristic", min_value=0.0, value=0.0, step=1.0, key="m4_agent_price_override")
        # reuse TCO heuristic for price if override zero
        avg_build = sum(float(st.session_state.get(f"tco_build_hours_{t.lower()}", DEFAULTS["tco_build_hours_utility"])) * float(st.session_state.get(f"tco_hourly_{t.lower()}", DEFAULTS["tco_hourly_utility"])) for t in AGENT_TYPES) / max(1, len(AGENT_TYPES))
        agent_price_default = (avg_build / 36.0) + ((sum(float(st.session_state.get(f"tco_maint_pct_{t.lower()}", DEFAULTS["tco_maintenance_pct_year"])) for t in AGENT_TYPES) / len(AGENT_TYPES)) * avg_build / 1200.0) + (float(st.session_state.get("tco_recurring_license_monthly", 0.0)) / max(1, int(st.session_state.get("tco_min_agents", 1))))
        agent_price_month = agent_price_default if agent_price_month_override <= 0 else agent_price_month_override
        st.markdown(f"- Agent price used (mo): **{currency(agent_price_month)}**")
        # approximate monthly agent hrs (prod hrs per agent default)
        agent_prod_hrs_mo = st.number_input("Agent prod hrs / month (per agent)", min_value=1, value=180, step=1, key="m4_agent_prod_hrs")
        agents_needed = math.ceil(agent_hours / (agent_prod_hrs_mo*12)) if agent_prod_hrs_mo>0 else 0
        total_agent_cost_ann = agents_needed * agent_price_month * 12
        human_cost_ann = human_hours * human_cost_hr
        st.markdown(f"- Agents needed (ann): **{agents_needed}**")
        st.markdown(f"- Total agent cost (ann): **{currency(total_agent_cost_ann)}**")
        st.markdown(f"- Human cost (ann): **{currency(human_cost_ann)}**")
        st.markdown(f"- Combined cost (ann): **{currency(total_agent_cost_ann + human_cost_ann)}**")

# -----------------------
# Home page with Agent Types quick reference
# -----------------------
def home_page():
    st.markdown(
        """
        <div style="background:linear-gradient(90deg,#012169,#0053b3);padding:12px;border-radius:8px;color:#fff">
           <h2 style="margin:0">Agent Pricing Factory</h2>
           <div style="font-size:14px;opacity:0.95">Quick tools: TCO -> Simulation -> Agent Efficiency -> Commercial Models</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("Use the left menu to navigate. Start with TCO to capture costs, then Simulation to model a project. Agent Efficiency and Models pages provide more scenario-specific tooling.")

    st.markdown("---")
    st.subheader("Agent Types — Quick Reference")
    # Example reference data, adapted from earlier conversation
    quick_ref = [
        {"Type": "Utility", "Description": "Small, simple automations. Low build cost, low savings", "ProductivityGain": "2-5%"},
        {"Type": "Standard", "Description": "Standard agent for common tasks. Moderate build cost", "ProductivityGain": "5-7%"},
        {"Type": "Professional", "Description": "Complex agents with integrations. Higher costs, higher gains", "ProductivityGain": "7-10%"},
        {"Type": "Enterprise", "Description": "Mission-critical agents, strong ROI over time", "ProductivityGain": "10-15%"},
    ]
    st.table(pd.DataFrame(quick_ref))

# -----------------------
# Router
# -----------------------
PAGES = {
    "Home": home_page,
    "TCO": tco_page,
    "Simulation": simulation_page,
    "Agent Efficiency": agent_efficiency_page,
    "Commercial Models": models_page,
}

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Choose page", list(PAGES.keys()))
PAGES[choice]()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Agent Pricing Factory — simplified delivery")
