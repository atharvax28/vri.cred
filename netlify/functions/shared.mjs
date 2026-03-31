// Shared data and scoring logic for VRI Credit Intelligence functions

// ── Demo GSTIN Data (5 synthetic MSMEs) ──
export const DEMO_GSTINS = {
  "27AABCM1234D1Z5": {
    gstin: "27AABCM1234D1Z5",
    legal_name: "Mehta Precision Components Pvt Ltd",
    trade_name: "Mehta Precision",
    state_code: "27",
    business_type: "pvt_ltd",
    registration_date: "2016-04-15",
    status: "Active",
    returns_filed_12m: 12,
    nil_returns_12m: 0,
    late_returns_12m: 0,
    avg_monthly_revenue: 2850000.0,
    revenue_trend_pct: 18.5,
    total_tax_paid_12m: 6156000.0,
    quarterly_revenue: [8100000, 8550000, 8900000, 8850000],
    years_in_business: 8.5,
    employee_count_est: 45,
    sector: "Manufacturing",
    sub_sector: "Auto Components",
    litigation_flags: [],
    compliance_notices: 0,
    existing_loans: 2,
    total_outstanding: 4500000.0,
    dpd_30_count: 0,
    dpd_60_count: 0,
    dpd_90_count: 0,
    credit_utilization_pct: 35.0,
  },
  "27XYZBN5678E2Z3": {
    gstin: "27XYZBN5678E2Z3",
    legal_name: "Bansal Textile Traders",
    trade_name: "Bansal Fabrics",
    state_code: "27",
    business_type: "proprietorship",
    registration_date: "2019-08-22",
    status: "Active",
    returns_filed_12m: 7,
    nil_returns_12m: 3,
    late_returns_12m: 4,
    avg_monthly_revenue: 420000.0,
    revenue_trend_pct: -28.3,
    total_tax_paid_12m: 756000.0,
    quarterly_revenue: [1800000, 1400000, 900000, 940000],
    years_in_business: 5.2,
    employee_count_est: 8,
    sector: "Textile",
    sub_sector: "Fabric Trading",
    litigation_flags: [
      "NCLT Case #2024/MH/1234 — Supplier dispute ₹12L",
      "GST Notice — Discrepancy in GSTR-2A vs GSTR-3B",
    ],
    compliance_notices: 2,
    existing_loans: 3,
    total_outstanding: 2800000.0,
    dpd_30_count: 3,
    dpd_60_count: 1,
    dpd_90_count: 1,
    credit_utilization_pct: 88.0,
  },
  "29PQRST9012F3Z7": {
    gstin: "29PQRST9012F3Z7",
    legal_name: "Shakti Digital Solutions LLP",
    trade_name: "Shakti Digital",
    state_code: "29",
    business_type: "partnership",
    registration_date: "2020-01-10",
    status: "Active",
    returns_filed_12m: 10,
    nil_returns_12m: 1,
    late_returns_12m: 2,
    avg_monthly_revenue: 1200000.0,
    revenue_trend_pct: 5.2,
    total_tax_paid_12m: 2592000.0,
    quarterly_revenue: [3400000, 3600000, 3700000, 3700000],
    years_in_business: 4.1,
    employee_count_est: 22,
    sector: "IT Services",
    sub_sector: "Software Development",
    litigation_flags: [],
    compliance_notices: 1,
    existing_loans: 1,
    total_outstanding: 1500000.0,
    dpd_30_count: 1,
    dpd_60_count: 0,
    dpd_90_count: 0,
    credit_utilization_pct: 52.0,
  },
  "33ABCFP7890G4Z1": {
    gstin: "33ABCFP7890G4Z1",
    legal_name: "Annapoorna Food Products",
    trade_name: "Annapoorna Foods",
    state_code: "33",
    business_type: "proprietorship",
    registration_date: "2021-06-05",
    status: "Active",
    returns_filed_12m: 12,
    nil_returns_12m: 0,
    late_returns_12m: 1,
    avg_monthly_revenue: 680000.0,
    revenue_trend_pct: 32.0,
    total_tax_paid_12m: 979200.0,
    quarterly_revenue: [1500000, 1800000, 2200000, 2640000],
    years_in_business: 3.5,
    employee_count_est: 12,
    sector: "Food Processing",
    sub_sector: "Packaged Foods",
    litigation_flags: [],
    compliance_notices: 0,
    existing_loans: 1,
    total_outstanding: 800000.0,
    dpd_30_count: 0,
    dpd_60_count: 0,
    dpd_90_count: 0,
    credit_utilization_pct: 28.0,
  },
  "07DEFGH3456H5Z9": {
    gstin: "07DEFGH3456H5Z9",
    legal_name: "Gupta & Sons General Trading",
    trade_name: "Gupta Trading Co",
    state_code: "07",
    business_type: "partnership",
    registration_date: "2017-07-01",
    status: "Suspended",
    returns_filed_12m: 4,
    nil_returns_12m: 5,
    late_returns_12m: 3,
    avg_monthly_revenue: 180000.0,
    revenue_trend_pct: -62.5,
    total_tax_paid_12m: 259200.0,
    quarterly_revenue: [900000, 600000, 300000, 360000],
    years_in_business: 7.5,
    employee_count_est: 4,
    sector: "Trading",
    sub_sector: "General Merchandise",
    litigation_flags: [
      "Income Tax Notice — AY 2023-24 demand ₹4.2L",
      "NCLT Case #2023/DL/5678 — Creditor petition",
      "Consumer Forum complaint #CF/2024/891",
    ],
    compliance_notices: 4,
    existing_loans: 4,
    total_outstanding: 6200000.0,
    dpd_30_count: 4,
    dpd_60_count: 3,
    dpd_90_count: 2,
    credit_utilization_pct: 95.0,
  },
};

// ── Sector risk premiums ──
const SECTOR_RISK_MAP = {
  Manufacturing: 0.15,
  "IT Services": 0.10,
  "Food Processing": 0.20,
  Textile: 0.30,
  Trading: 0.35,
  Construction: 0.40,
  Healthcare: 0.12,
  Education: 0.18,
};

// ── Grade thresholds ──
const GRADE_THRESHOLDS = [
  [850, "A+"], [750, "A"], [650, "B+"], [550, "B"],
  [450, "C+"], [350, "C"], [250, "D+"], [0, "D"],
];

// ── Feature display names ──
const FEATURE_DISPLAY_NAMES = {
  filing_rate: "GST Filing Rate",
  nil_return_rate: "Nil Return Frequency",
  late_filing_rate: "Late Filing Frequency",
  filing_consistency_score: "Filing Consistency",
  is_active: "GST Registration Status",
  months_since_registration: "Time Since Registration",
  avg_monthly_revenue_log: "Monthly Revenue (scale)",
  revenue_trend_pct: "Revenue Growth Trend",
  revenue_volatility: "Revenue Volatility",
  quarterly_growth_rate: "Quarterly Growth",
  tax_to_revenue_ratio: "Tax/Revenue Ratio",
  revenue_per_employee: "Revenue per Employee",
  annualized_revenue_log: "Annual Revenue (scale)",
  is_revenue_declining: "Revenue Declining Flag",
  years_in_business: "Years in Business",
  business_maturity_score: "Business Maturity",
  employee_count_log: "Employee Count (scale)",
  is_proprietorship: "Proprietorship Type",
  is_partnership: "Partnership Type",
  is_pvt_ltd: "Pvt Ltd Type",
  existing_loan_count: "Existing Loans",
  total_outstanding_log: "Total Outstanding (scale)",
  dpd_30_count: "DPD 30+ Count",
  dpd_60_count: "DPD 60+ Count",
  dpd_90_count: "DPD 90+ Count",
  credit_utilization_pct: "Credit Utilization %",
  litigation_count: "Active Litigations",
  compliance_notice_count: "Compliance Notices",
  has_nclt_case: "NCLT Case Flag",
  has_tax_notice: "Tax Notice Flag",
  related_party_count: "Related Parties",
  risk_flag_density: "Risk Flag Density",
  is_suspended_or_cancelled: "Suspended/Cancelled Flag",
  debt_to_revenue_ratio: "Debt-to-Revenue Ratio",
  repayment_capacity_score: "Repayment Capacity",
  overall_compliance_score: "Overall Compliance",
  business_stability_index: "Business Stability",
  credit_risk_composite: "Credit Risk Composite",
  growth_momentum_score: "Growth Momentum",
  sector_risk_premium: "Sector Risk Premium",
};

// ── Feature weights for scoring (derived from XGBoost model importance) ──
const FEATURE_WEIGHTS = {
  filing_rate: 0.08,
  nil_return_rate: -0.06,
  late_filing_rate: -0.05,
  filing_consistency_score: 0.07,
  is_active: 0.10,
  months_since_registration: 0.02,
  avg_monthly_revenue_log: 0.06,
  revenue_trend_pct: 0.04,
  revenue_volatility: -0.03,
  quarterly_growth_rate: 0.03,
  tax_to_revenue_ratio: 0.02,
  revenue_per_employee: 0.02,
  annualized_revenue_log: 0.04,
  is_revenue_declining: -0.05,
  years_in_business: 0.03,
  business_maturity_score: 0.04,
  employee_count_log: 0.02,
  is_proprietorship: -0.01,
  is_partnership: 0.0,
  is_pvt_ltd: 0.02,
  existing_loan_count: -0.02,
  total_outstanding_log: -0.03,
  dpd_30_count: -0.06,
  dpd_60_count: -0.08,
  dpd_90_count: -0.10,
  credit_utilization_pct: -0.05,
  litigation_count: -0.06,
  compliance_notice_count: -0.04,
  has_nclt_case: -0.07,
  has_tax_notice: -0.04,
  related_party_count: 0.01,
  risk_flag_density: -0.05,
  is_suspended_or_cancelled: -0.12,
  debt_to_revenue_ratio: -0.04,
  repayment_capacity_score: 0.06,
  overall_compliance_score: 0.07,
  business_stability_index: 0.06,
  credit_risk_composite: -0.08,
  growth_momentum_score: 0.05,
  sector_risk_premium: -0.03,
};

function sigmoid(x) {
  return 1.0 / (1.0 + Math.exp(-x));
}

function safeLog(val, base = 10) {
  return Math.log(Math.max(val, 1.0)) / Math.log(base);
}

function revenueVolatility(quarterly) {
  if (!quarterly || quarterly.length < 2) return 0.0;
  const mean = quarterly.reduce((a, b) => a + b, 0) / quarterly.length;
  if (mean === 0) return 1.0;
  const variance = quarterly.reduce((acc, q) => acc + (q - mean) ** 2, 0) / quarterly.length;
  return Math.sqrt(variance) / mean;
}

export function extractFeatures(data) {
  const filingRate = data.returns_filed_12m / 12.0;
  const nilReturnRate = data.nil_returns_12m / 12.0;
  const lateFilingRate = data.late_returns_12m / 12.0;
  const filingConsistency = filingRate * (1 - nilReturnRate) * (1 - lateFilingRate * 0.5);
  const isActive = data.status === "Active" ? 1.0 : 0.0;
  const monthsSinceReg = data.years_in_business * 12;

  const avgRevLog = safeLog(data.avg_monthly_revenue + 1);
  const revVol = revenueVolatility(data.quarterly_revenue);
  const qRev = data.quarterly_revenue;
  const quarterlyGrowth = qRev && qRev[0] > 0 ? qRev[qRev.length - 1] / qRev[0] - 1.0 : 0.0;
  const annualRevenue = data.avg_monthly_revenue * 12;
  const taxRatio = data.total_tax_paid_12m / Math.max(annualRevenue, 1.0);
  const revPerEmp = data.avg_monthly_revenue / Math.max(data.employee_count_est, 1);
  const annRevLog = safeLog(annualRevenue + 1);
  const isDeclining = data.revenue_trend_pct < -10.0 ? 1.0 : 0.0;

  const maturity = sigmoid(data.years_in_business - 3.0);
  const empLog = safeLog(data.employee_count_est + 1, 2.0);
  const isProp = data.business_type === "proprietorship" ? 1.0 : 0.0;
  const isPart = data.business_type === "partnership" ? 1.0 : 0.0;
  const isPvt = data.business_type === "pvt_ltd" ? 1.0 : 0.0;

  const outstandingLog = safeLog(data.total_outstanding + 1);

  const litCount = data.litigation_flags.length;
  const hasNclt = data.litigation_flags.some((f) => f.toLowerCase().includes("nclt")) ? 1.0 : 0.0;
  const hasTax = data.litigation_flags.some(
    (f) => f.toLowerCase().includes("tax notice") || f.toLowerCase().includes("income tax")
  ) ? 1.0 : 0.0;
  const relatedCount = 0; // not exposed in detail response
  const riskDensity = (litCount + data.compliance_notices) / Math.max(data.years_in_business, 0.5);
  const isSuspended = ["Suspended", "Cancelled"].includes(data.status) ? 1.0 : 0.0;

  const debtToRev = data.total_outstanding / Math.max(annualRevenue, 1.0);
  const repaymentRaw = avgRevLog * 0.4 - outstandingLog * 0.3 - data.dpd_90_count * 0.2 - (data.credit_utilization_pct / 100) * 0.1;
  const repaymentScore = sigmoid(repaymentRaw);
  const complianceScore = filingConsistency * 0.6 + (1.0 - Math.min(data.compliance_notices, 5) / 5.0) * 0.4;
  const stability = maturity * 0.4 + (1.0 - revVol) * 0.3 + filingRate * 0.3;
  const creditRisk = data.dpd_30_count * 0.15 + data.dpd_60_count * 0.25 + data.dpd_90_count * 0.40 + (data.credit_utilization_pct / 100) * 0.20;
  const growthMomentum = sigmoid(data.revenue_trend_pct / 20 + quarterlyGrowth);
  const sectorRisk = SECTOR_RISK_MAP[data.sector] || 0.25;

  return {
    filing_rate: filingRate,
    nil_return_rate: nilReturnRate,
    late_filing_rate: lateFilingRate,
    filing_consistency_score: filingConsistency,
    is_active: isActive,
    months_since_registration: monthsSinceReg,
    avg_monthly_revenue_log: avgRevLog,
    revenue_trend_pct: data.revenue_trend_pct,
    revenue_volatility: revVol,
    quarterly_growth_rate: quarterlyGrowth,
    tax_to_revenue_ratio: taxRatio,
    revenue_per_employee: revPerEmp,
    annualized_revenue_log: annRevLog,
    is_revenue_declining: isDeclining,
    years_in_business: data.years_in_business,
    business_maturity_score: maturity,
    employee_count_log: empLog,
    is_proprietorship: isProp,
    is_partnership: isPart,
    is_pvt_ltd: isPvt,
    existing_loan_count: data.existing_loans,
    total_outstanding_log: outstandingLog,
    dpd_30_count: data.dpd_30_count,
    dpd_60_count: data.dpd_60_count,
    dpd_90_count: data.dpd_90_count,
    credit_utilization_pct: data.credit_utilization_pct,
    litigation_count: litCount,
    compliance_notice_count: data.compliance_notices,
    has_nclt_case: hasNclt,
    has_tax_notice: hasTax,
    related_party_count: relatedCount,
    risk_flag_density: riskDensity,
    is_suspended_or_cancelled: isSuspended,
    debt_to_revenue_ratio: debtToRev,
    repayment_capacity_score: repaymentScore,
    overall_compliance_score: complianceScore,
    business_stability_index: stability,
    credit_risk_composite: creditRisk,
    growth_momentum_score: growthMomentum,
    sector_risk_premium: sectorRisk,
  };
}

function scoreToGrade(score) {
  for (const [threshold, grade] of GRADE_THRESHOLDS) {
    if (score >= threshold) return grade;
  }
  return "D";
}

export function scoreGstin(data) {
  const features = extractFeatures(data);

  // Weighted feature scoring (replicates XGBoost model behavior for demo data)
  let rawScore = 0.5; // base
  for (const [feature, weight] of Object.entries(FEATURE_WEIGHTS)) {
    const val = features[feature] || 0;
    // Normalize feature contribution
    rawScore += weight * val * 0.1;
  }

  // Clamp PD
  const pd = Math.max(0.01, Math.min(0.99, 1.0 - sigmoid(rawScore * 4 - 2)));
  const vriScore = Math.max(0, Math.min(1000, Math.round((1.0 - pd) * 1000)));
  const riskGrade = scoreToGrade(vriScore);

  // Compute SHAP-like explanations (feature contribution to score)
  const shapFactors = Object.entries(features)
    .map(([feature, value]) => {
      const weight = FEATURE_WEIGHTS[feature] || 0;
      const shapValue = weight * value * 0.1;
      return {
        feature,
        display_name: FEATURE_DISPLAY_NAMES[feature] || feature,
        value: Math.round(value * 10000) / 10000,
        shap_value: Math.round(shapValue * 10000) / 10000,
        direction: shapValue >= 0 ? "positive" : "negative",
        magnitude: Math.abs(shapValue) > 0.1 ? "high" : Math.abs(shapValue) > 0.03 ? "medium" : "low",
      };
    })
    .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
    .slice(0, 10);

  return {
    gstin: data.gstin,
    legal_name: data.legal_name,
    trade_name: data.trade_name,
    vri_score: vriScore,
    risk_grade: riskGrade,
    probability_of_default: Math.round(pd * 10000) / 10000,
    shap_factors: shapFactors,
    model_version: "demo-v1.0",
  };
}

export function formatCurrencyInr(amount) {
  if (amount < 0) return `-₹${formatCurrencyInr(Math.abs(amount)).slice(1)}`;
  const intPart = Math.floor(amount);
  const decPart = (amount - intPart).toFixed(2).slice(1);
  const s = String(intPart);
  if (s.length <= 3) return `₹${s}${decPart}`;
  const lastThree = s.slice(-3);
  let remaining = s.slice(0, -3);
  const groups = [];
  while (remaining) {
    groups.push(remaining.slice(-2));
    remaining = remaining.slice(0, -2);
  }
  groups.reverse();
  return `₹${groups.join(",")},${lastThree}${decPart}`;
}

export function generateTemplateReport(scoring, data) {
  const isGood = scoring.vri_score >= 600;
  const isBorderline = scoring.vri_score >= 400 && scoring.vri_score < 600;

  let executiveSummary, recommendation;

  if (isGood) {
    executiveSummary = `${data.trade_name} demonstrates strong creditworthiness with a VRI score of ${scoring.vri_score}/1000 (Grade ${scoring.risk_grade}). The business shows consistent GST compliance, stable revenue growth of ${data.revenue_trend_pct > 0 ? "+" : ""}${data.revenue_trend_pct.toFixed(1)}%, and a healthy credit utilization of ${data.credit_utilization_pct}%.`;
    recommendation = `APPROVE — Recommended credit limit up to ${formatCurrencyInr(data.avg_monthly_revenue * 3)} with standard terms.`;
  } else if (isBorderline) {
    executiveSummary = `${data.trade_name} presents a borderline credit profile with a VRI score of ${scoring.vri_score}/1000 (Grade ${scoring.risk_grade}). While the business has operational history, certain risk factors warrant enhanced due diligence.`;
    recommendation = `CONDITIONAL APPROVE — Reduced credit limit up to ${formatCurrencyInr(data.avg_monthly_revenue * 1.5)} with enhanced monitoring and quarterly review.`;
  } else {
    executiveSummary = `${data.trade_name} presents significant credit risk with a VRI score of ${scoring.vri_score}/1000 (Grade ${scoring.risk_grade}). Multiple risk factors including ${data.credit_utilization_pct > 75 ? "high debt levels, " : ""}${data.revenue_trend_pct < -10 ? "declining revenue, " : ""}indicate elevated default probability.`;
    recommendation = "REJECT — Credit application does not meet minimum eligibility criteria at this time.";
  }

  return {
    gstin: data.gstin,
    legal_name: data.legal_name,
    trade_name: data.trade_name,
    vri_score: scoring.vri_score,
    risk_grade: scoring.risk_grade,
    probability_of_default: scoring.probability_of_default,
    executive_summary: executiveSummary,
    business_overview: `${data.trade_name} (${data.legal_name}) is a ${data.business_type} operating in ${data.sector}/${data.sub_sector} since ${data.registration_date}. The business employs approximately ${data.employee_count_est} people and generates average monthly revenue of ${formatCurrencyInr(data.avg_monthly_revenue)}.`,
    financial_analysis: `Annual revenue stands at approximately ${formatCurrencyInr(data.avg_monthly_revenue * 12)} with a year-over-year trend of ${data.revenue_trend_pct > 0 ? "+" : ""}${data.revenue_trend_pct.toFixed(1)}%. GST compliance is ${data.returns_filed_12m >= 10 ? "strong" : data.returns_filed_12m >= 7 ? "moderate" : "weak"} with ${data.returns_filed_12m}/12 returns filed on time. Total tax paid in the last 12 months is ${formatCurrencyInr(data.total_tax_paid_12m)}, indicating ${data.nil_returns_12m <= 1 ? "consistent" : "inconsistent"} business activity.`,
    risk_factors: `Key risk factors include: credit utilization at ${data.credit_utilization_pct}%, ${data.existing_loans} existing loans with total outstanding of ${formatCurrencyInr(data.total_outstanding)}. ${data.litigation_flags.length > 0 ? "Active litigation(s) noted. " : ""}${data.dpd_30_count > 0 ? "DPD events detected in credit history. " : ""}${data.status !== "Active" ? "GST registration is not Active — major red flag." : ""}`,
    strengths: `Positive indicators: ${data.years_in_business.toFixed(1)} years of operational history, ${data.returns_filed_12m >= 10 ? "strong GST filing compliance, " : ""}${data.revenue_trend_pct > 10 ? "positive revenue growth trend, " : ""}${data.litigation_flags.length === 0 ? "clean litigation record, " : ""}${data.credit_utilization_pct < 50 ? "low credit utilization" : "established banking relationship"}.`,
    recommendation,
    shap_top_factors: scoring.shap_factors.map((f) => ({
      feature: f.feature,
      display_name: f.display_name,
      value: f.value,
      shap_value: f.shap_value,
      direction: f.direction,
      magnitude: f.magnitude,
    })),
    model_version: scoring.model_version,
    generated_at: new Date().toISOString(),
    disclaimer:
      "This credit assessment is generated by an AI system and is intended as a decision-support tool only. It should not be used as the sole basis for credit decisions. All assessments must be reviewed by qualified credit officers in accordance with RBI Master Direction on Digital Lending (RBI/2022-23/111) and institutional credit policies.",
  };
}
