/*
 * PectinHydrolysisTwin - FMI 2.0 Co-Simulation Implementation
 * 4-Pool Mechanistic Pectin Acid Hydrolysis Digital Twin
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "fmi2Functions.h"

#define MODEL_GUID "{7e14d3ba-a476-4d05-9f5b-59d870c91834}"
#define MODEL_IDENTIFIER "PectinHydrolysisTwin"
#define GAS_CONSTANT 8.31446261815324
#define T_REF_KELVIN 353.15 /* 80 deg C */
#define H_REF 0.01          /* 10^(-2.0) */

/* Value references matching modelDescription.xml */
enum ValueReference {
    /* Parameters */
    vr_T_reactor       = 0,
    vr_pH_reactor      = 1,
    vr_C_citric        = 2,
    vr_dry_matter_mass = 3,
    vr_pectin_mass_0   = 4,
    vr_k_ref_ext       = 5,
    vr_Ea_ext          = 6,
    vr_k_ref_hyd       = 7,
    vr_Ea_hyd          = 8,
    vr_k_ref_deg       = 9,
    vr_Ea_deg          = 10,
    vr_k_ref_de        = 11,
    vr_Ea_de           = 12,
    vr_Mw_matrix_0     = 13,
    vr_DE_matrix_0     = 14,
    vr_recovery_eff    = 15,

    /* Continuous States */
    vr_P_matrix        = 20,
    vr_P_sol           = 21,
    vr_P_lowMW         = 22,
    vr_P_loss          = 23,
    vr_Q_DE_sol        = 24,
    vr_Q_MW_sol        = 25,

    /* Observables */
    vr_yield_pct       = 30,
    vr_P_product       = 31,
    vr_DE_sol          = 32,
    vr_Mw_sol          = 33,
    vr_P_tot           = 34
};

typedef struct {
    /* Parameters */
    fmi2Real T_reactor;
    fmi2Real pH_reactor;
    fmi2Real C_citric;
    fmi2Real dry_matter_mass;
    fmi2Real pectin_mass_0;
    fmi2Real k_ref_ext;
    fmi2Real Ea_ext;
    fmi2Real k_ref_hyd;
    fmi2Real Ea_hyd;
    fmi2Real k_ref_deg;
    fmi2Real Ea_deg;
    fmi2Real k_ref_de;
    fmi2Real Ea_de;
    fmi2Real Mw_matrix_0;
    fmi2Real DE_matrix_0;
    fmi2Real recovery_eff;

    /* Continuous States */
    fmi2Real P_matrix;
    fmi2Real P_sol;
    fmi2Real P_lowMW;
    fmi2Real P_loss;
    fmi2Real Q_DE_sol;
    fmi2Real Q_MW_sol;

    /* Observables */
    fmi2Real yield_pct;
    fmi2Real P_product;
    fmi2Real DE_sol;
    fmi2Real Mw_sol;
    fmi2Real P_tot;

    /* Time */
    fmi2Real time;

    /* FMI Infrastructure */
    fmi2String instanceName;
    fmi2CallbackFunctions callbacks;
    fmi2Boolean loggingOn;
} ModelInstance;

static void update_observables(ModelInstance* comp) {
    fmi2Real p_sol_safe = (comp->P_sol > 1e-12) ? comp->P_sol : 1e-12;
    comp->DE_sol = comp->Q_DE_sol / p_sol_safe;
    comp->Mw_sol = comp->Q_MW_sol / p_sol_safe;
    comp->P_product = comp->recovery_eff * (comp->P_sol + comp->P_lowMW);
    comp->yield_pct = (comp->P_product / comp->pectin_mass_0) * 100.0;
    comp->P_tot = comp->P_matrix + comp->P_sol + comp->P_lowMW + comp->P_loss;
}

static void compute_derivatives(ModelInstance* comp, const fmi2Real y[6], fmi2Real dydt[6]) {
    fmi2Real T_kelvin = comp->T_reactor + 273.15;
    fmi2Real H_plus = pow(10.0, -comp->pH_reactor);

    /* Arrhenius rate multipliers */
    fmi2Real arr_ext = exp(-(comp->Ea_ext / GAS_CONSTANT) * (1.0 / T_kelvin - 1.0 / T_REF_KELVIN));
    fmi2Real arr_hyd = exp(-(comp->Ea_hyd / GAS_CONSTANT) * (1.0 / T_kelvin - 1.0 / T_REF_KELVIN));
    fmi2Real arr_deg = exp(-(comp->Ea_deg / GAS_CONSTANT) * (1.0 / T_kelvin - 1.0 / T_REF_KELVIN));
    fmi2Real arr_de  = exp(-(comp->Ea_de  / GAS_CONSTANT) * (1.0 / T_kelvin - 1.0 / T_REF_KELVIN));

    /* Effective rate constants [1/sec] (converted from 1/min) */
    fmi2Real k_ext = (comp->k_ref_ext * arr_ext) / 60.0;
    fmi2Real k_hyd = (comp->k_ref_hyd * arr_hyd * (H_plus / H_REF)) / 60.0;
    fmi2Real k_deg = (comp->k_ref_deg * arr_deg * (H_plus / H_REF)) / 60.0;
    fmi2Real k_de  = (comp->k_ref_de  * arr_de) / 60.0;

    fmi2Real p_matrix = (y[0] > 0.0) ? y[0] : 0.0;
    fmi2Real p_sol    = (y[1] > 0.0) ? y[1] : 0.0;
    fmi2Real p_lowMW  = (y[2] > 0.0) ? y[2] : 0.0;
    fmi2Real q_de     = y[4];
    fmi2Real q_mw     = y[5];

    /* ODEs */
    dydt[0] = -k_ext * p_matrix;
    dydt[1] = k_ext * p_matrix - k_hyd * p_sol;
    dydt[2] = k_hyd * p_sol - k_deg * p_lowMW;
    dydt[3] = k_deg * p_lowMW;
    dydt[4] = k_ext * comp->DE_matrix_0 * p_matrix - (k_hyd + k_de) * q_de;
    dydt[5] = k_ext * comp->Mw_matrix_0 * p_matrix - 2.0 * k_hyd * q_mw;
}

/* 4th-order Runge-Kutta numerical integration step */
static void rk4_step(ModelInstance* comp, fmi2Real dt) {
    fmi2Real y[6], k1[6], k2[6], k3[6], k4[6], y_temp[6];
    int i;

    y[0] = comp->P_matrix;
    y[1] = comp->P_sol;
    y[2] = comp->P_lowMW;
    y[3] = comp->P_loss;
    y[4] = comp->Q_DE_sol;
    y[5] = comp->Q_MW_sol;

    compute_derivatives(comp, y, k1);

    for (i = 0; i < 6; i++) y_temp[i] = y[i] + 0.5 * dt * k1[i];
    compute_derivatives(comp, y_temp, k2);

    for (i = 0; i < 6; i++) y_temp[i] = y[i] + 0.5 * dt * k2[i];
    compute_derivatives(comp, y_temp, k3);

    for (i = 0; i < 6; i++) y_temp[i] = y[i] + dt * k3[i];
    compute_derivatives(comp, y_temp, k4);

    comp->P_matrix += (dt / 6.0) * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]);
    comp->P_sol    += (dt / 6.0) * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]);
    comp->P_lowMW  += (dt / 6.0) * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]);
    comp->P_loss   += (dt / 6.0) * (k1[3] + 2.0 * k2[3] + 2.0 * k3[3] + k4[3]);
    comp->Q_DE_sol += (dt / 6.0) * (k1[4] + 2.0 * k2[4] + 2.0 * k3[4] + k4[4]);
    comp->Q_MW_sol += (dt / 6.0) * (k1[5] + 2.0 * k2[5] + 2.0 * k3[5] + k4[5]);

    update_observables(comp);
}

/***************************************************
 * FMI 2.0 Standard Functions
 ***************************************************/

FMI2_Export const char* fmi2GetTypesPlatform(void) {
    return fmi2TypesPlatform;
}

FMI2_Export const char* fmi2GetVersion(void) {
    return fmi2Version;
}

FMI2_Export fmi2Component fmi2Instantiate(
    fmi2String instanceName,
    fmi2Type type,
    fmi2String guid,
    fmi2String resourceLocation,
    const fmi2CallbackFunctions* functions,
    fmi2Boolean visible,
    fmi2Boolean loggingOn
) {
    ModelInstance* comp;
    (void)type;
    (void)resourceLocation;
    (void)visible;

    if (!guid || strcmp(guid, MODEL_GUID) != 0) return NULL;
    if (!functions) return NULL;

    comp = (ModelInstance*)calloc(1, sizeof(ModelInstance));
    if (!comp) return NULL;

    comp->instanceName = strdup(instanceName);
    comp->callbacks = *functions;
    comp->loggingOn = loggingOn;

    /* Default parameter values */
    comp->T_reactor       = 80.0;
    comp->pH_reactor      = 2.0;
    comp->C_citric        = 0.05;
    comp->dry_matter_mass = 1.0;
    comp->pectin_mass_0   = 0.2333;
    comp->k_ref_ext       = 0.035;
    comp->Ea_ext          = 60000.0;
    comp->k_ref_hyd       = 0.015;
    comp->Ea_hyd          = 85000.0;
    comp->k_ref_deg       = 0.005;
    comp->Ea_deg          = 100000.0;
    comp->k_ref_de        = 0.012;
    comp->Ea_de           = 50000.0;
    comp->Mw_matrix_0     = 654000.0;
    comp->DE_matrix_0     = 0.745;
    comp->recovery_eff    = 0.90;

    /* Default initial state */
    comp->P_matrix        = 0.2333;
    comp->P_sol           = 0.0;
    comp->P_lowMW         = 0.0;
    comp->P_loss          = 0.0;
    comp->Q_DE_sol        = 0.0;
    comp->Q_MW_sol        = 0.0;
    comp->time            = 0.0;

    update_observables(comp);
    return (fmi2Component)comp;
}

FMI2_Export void fmi2FreeInstance(fmi2Component c) {
    ModelInstance* comp = (ModelInstance*)c;
    if (comp) {
        if (comp->instanceName) free((void*)comp->instanceName);
        free(comp);
    }
}

FMI2_Export fmi2Status fmi2SetupExperiment(
    fmi2Component c,
    fmi2Boolean toleranceDefined,
    fmi2Real tolerance,
    fmi2Real startTime,
    fmi2Boolean stopTimeDefined,
    fmi2Real stopTime
) {
    ModelInstance* comp = (ModelInstance*)c;
    (void)toleranceDefined;
    (void)tolerance;
    (void)stopTimeDefined;
    (void)stopTime;
    if (!comp) return fmi2Error;
    comp->time = startTime;
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2EnterInitializationMode(fmi2Component c) {
    (void)c;
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2ExitInitializationMode(fmi2Component c) {
    ModelInstance* comp = (ModelInstance*)c;
    if (!comp) return fmi2Error;
    comp->P_matrix = comp->pectin_mass_0;
    comp->P_sol = 0.0;
    comp->P_lowMW = 0.0;
    comp->P_loss = 0.0;
    comp->Q_DE_sol = 0.0;
    comp->Q_MW_sol = 0.0;
    update_observables(comp);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2Terminate(fmi2Component c) {
    (void)c;
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2Reset(fmi2Component c) {
    ModelInstance* comp = (ModelInstance*)c;
    if (!comp) return fmi2Error;
    comp->time = 0.0;
    comp->P_matrix = comp->pectin_mass_0;
    comp->P_sol = 0.0;
    comp->P_lowMW = 0.0;
    comp->P_loss = 0.0;
    comp->Q_DE_sol = 0.0;
    comp->Q_MW_sol = 0.0;
    update_observables(comp);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2GetReal(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    fmi2Real value[]
) {
    ModelInstance* comp = (ModelInstance*)c;
    size_t i;
    if (!comp) return fmi2Error;

    for (i = 0; i < nvr; i++) {
        switch (vr[i]) {
            case vr_T_reactor:       value[i] = comp->T_reactor; break;
            case vr_pH_reactor:      value[i] = comp->pH_reactor; break;
            case vr_C_citric:        value[i] = comp->C_citric; break;
            case vr_dry_matter_mass: value[i] = comp->dry_matter_mass; break;
            case vr_pectin_mass_0:   value[i] = comp->pectin_mass_0; break;
            case vr_k_ref_ext:       value[i] = comp->k_ref_ext; break;
            case vr_Ea_ext:          value[i] = comp->Ea_ext; break;
            case vr_k_ref_hyd:       value[i] = comp->k_ref_hyd; break;
            case vr_Ea_hyd:          value[i] = comp->Ea_hyd; break;
            case vr_k_ref_deg:       value[i] = comp->k_ref_deg; break;
            case vr_Ea_deg:          value[i] = comp->Ea_deg; break;
            case vr_k_ref_de:        value[i] = comp->k_ref_de; break;
            case vr_Ea_de:           value[i] = comp->Ea_de; break;
            case vr_Mw_matrix_0:     value[i] = comp->Mw_matrix_0; break;
            case vr_DE_matrix_0:     value[i] = comp->DE_matrix_0; break;
            case vr_recovery_eff:    value[i] = comp->recovery_eff; break;
            case vr_P_matrix:        value[i] = comp->P_matrix; break;
            case vr_P_sol:           value[i] = comp->P_sol; break;
            case vr_P_lowMW:         value[i] = comp->P_lowMW; break;
            case vr_P_loss:          value[i] = comp->P_loss; break;
            case vr_Q_DE_sol:        value[i] = comp->Q_DE_sol; break;
            case vr_Q_MW_sol:        value[i] = comp->Q_MW_sol; break;
            case vr_yield_pct:       value[i] = comp->yield_pct; break;
            case vr_P_product:       value[i] = comp->P_product; break;
            case vr_DE_sol:          value[i] = comp->DE_sol; break;
            case vr_Mw_sol:          value[i] = comp->Mw_sol; break;
            case vr_P_tot:           value[i] = comp->P_tot; break;
            default: return fmi2Error;
        }
    }
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2SetReal(
    fmi2Component c,
    const fmi2ValueReference vr[],
    size_t nvr,
    const fmi2Real value[]
) {
    ModelInstance* comp = (ModelInstance*)c;
    size_t i;
    if (!comp) return fmi2Error;

    for (i = 0; i < nvr; i++) {
        switch (vr[i]) {
            case vr_T_reactor:       comp->T_reactor = value[i]; break;
            case vr_pH_reactor:      comp->pH_reactor = value[i]; break;
            case vr_C_citric:        comp->C_citric = value[i]; break;
            case vr_dry_matter_mass: comp->dry_matter_mass = value[i]; break;
            case vr_pectin_mass_0:   comp->pectin_mass_0 = value[i]; break;
            case vr_k_ref_ext:       comp->k_ref_ext = value[i]; break;
            case vr_Ea_ext:          comp->Ea_ext = value[i]; break;
            case vr_k_ref_hyd:       comp->k_ref_hyd = value[i]; break;
            case vr_Ea_hyd:          comp->Ea_hyd = value[i]; break;
            case vr_k_ref_deg:       comp->k_ref_deg = value[i]; break;
            case vr_Ea_deg:          comp->Ea_deg = value[i]; break;
            case vr_k_ref_de:        comp->k_ref_de = value[i]; break;
            case vr_Ea_de:           comp->Ea_de = value[i]; break;
            case vr_Mw_matrix_0:     comp->Mw_matrix_0 = value[i]; break;
            case vr_DE_matrix_0:     comp->DE_matrix_0 = value[i]; break;
            case vr_recovery_eff:    comp->recovery_eff = value[i]; break;
            case vr_P_matrix:        comp->P_matrix = value[i]; break;
            case vr_P_sol:           comp->P_sol = value[i]; break;
            case vr_P_lowMW:         comp->P_lowMW = value[i]; break;
            case vr_P_loss:          comp->P_loss = value[i]; break;
            case vr_Q_DE_sol:        comp->Q_DE_sol = value[i]; break;
            case vr_Q_MW_sol:        comp->Q_MW_sol = value[i]; break;
            default: return fmi2Error;
        }
    }
    update_observables(comp);
    return fmi2OK;
}

FMI2_Export fmi2Status fmi2DoStep(
    fmi2Component c,
    fmi2Real currentCommunicationPoint,
    fmi2Real communicationStepSize,
    fmi2Boolean noSetFMUStatePriorToCurrentPoint
) {
    ModelInstance* comp = (ModelInstance*)c;
    fmi2Real remaining = communicationStepSize;
    fmi2Real substep = 0.5; /* 0.5 second substep for RK4 stability */
    (void)currentCommunicationPoint;
    (void)noSetFMUStatePriorToCurrentPoint;

    if (!comp) return fmi2Error;

    while (remaining > 1e-9) {
        fmi2Real h = (remaining > substep) ? substep : remaining;
        rk4_step(comp, h);
        remaining -= h;
    }
    comp->time += communicationStepSize;
    return fmi2OK;
}

/* Stubs for unused types */
FMI2_Export fmi2Status fmi2GetInteger(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Integer value[]) { (void)c; (void)vr; (void)nvr; (void)value; return fmi2OK; }
FMI2_Export fmi2Status fmi2SetInteger(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer value[]) { (void)c; (void)vr; (void)nvr; (void)value; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetBoolean(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Boolean value[]) { (void)c; (void)vr; (void)nvr; (void)value; return fmi2OK; }
FMI2_Export fmi2Status fmi2SetBoolean(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Boolean value[]) { (void)c; (void)vr; (void)nvr; (void)value; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetString(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2String value[]) { (void)c; (void)vr; (void)nvr; (void)value; return fmi2OK; }
FMI2_Export fmi2Status fmi2SetString(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2String value[]) { (void)c; (void)vr; (void)nvr; (void)value; return fmi2OK; }
FMI2_Export fmi2Status fmi2SetDebugLogging(fmi2Component c, fmi2Boolean loggingOn, size_t nCategories, const fmi2String categories[]) { (void)c; (void)loggingOn; (void)nCategories; (void)categories; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetFMUstate(fmi2Component c, fmi2FMUstate* s) { (void)c; (void)s; return fmi2Error; }
FMI2_Export fmi2Status fmi2SetFMUstate(fmi2Component c, fmi2FMUstate s) { (void)c; (void)s; return fmi2Error; }
FMI2_Export fmi2Status fmi2FreeFMUstate(fmi2Component c, fmi2FMUstate* s) { (void)c; (void)s; return fmi2Error; }
FMI2_Export fmi2Status fmi2SerializedFMUstateSize(fmi2Component c, fmi2FMUstate s, size_t* size) { (void)c; (void)s; (void)size; return fmi2Error; }
FMI2_Export fmi2Status fmi2SerializeFMUstate(fmi2Component c, fmi2FMUstate s, fmi2Byte serializedState[], size_t size) { (void)c; (void)s; (void)serializedState; (void)size; return fmi2Error; }
FMI2_Export fmi2Status fmi2DeSerializeFMUstate(fmi2Component c, const fmi2Byte serializedState[], size_t size, fmi2FMUstate* s) { (void)c; (void)serializedState; (void)size; (void)s; return fmi2Error; }
FMI2_Export fmi2Status fmi2GetDirectionalDerivative(fmi2Component c, const fmi2ValueReference vUnknown_ref[], size_t nUnknown, const fmi2ValueReference vKnown_ref[], size_t nKnown, const fmi2Real dvKnown[], fmi2Real dvUnknown[]) { (void)c; (void)vUnknown_ref; (void)nUnknown; (void)vKnown_ref; (void)nKnown; (void)dvKnown; (void)dvUnknown; return fmi2Error; }
FMI2_Export fmi2Status fmi2CancelStep(fmi2Component c) { (void)c; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetStatus(fmi2Component c, const fmi2StatusKind s, fmi2Status* value) { (void)c; (void)s; if (value) *value = fmi2OK; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetRealStatus(fmi2Component c, const fmi2StatusKind s, fmi2Real* value) { (void)c; (void)s; if (value) *value = 0.0; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetIntegerStatus(fmi2Component c, const fmi2StatusKind s, fmi2Integer* value) { (void)c; (void)s; if (value) *value = 0; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetBooleanStatus(fmi2Component c, const fmi2StatusKind s, fmi2Boolean* value) { (void)c; (void)s; if (value) *value = fmi2False; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetStringStatus(fmi2Component c, const fmi2StatusKind s, fmi2String* value) { (void)c; (void)s; if (value) *value = ""; return fmi2OK; }
FMI2_Export fmi2Status fmi2SetRealInputDerivatives(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer order[], const fmi2Real value[]) { (void)c; (void)vr; (void)nvr; (void)order; (void)value; return fmi2OK; }
FMI2_Export fmi2Status fmi2GetRealOutputDerivatives(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer order[], fmi2Real value[]) { (void)c; (void)vr; (void)nvr; (void)order; (void)value; return fmi2OK; }
