
/*
Source:
https://www.iaa.ie/docs/default-source/publications/advisory-memoranda/uas-advisory-memoranda-(uam)/uam-008---guidance-on-defining-flight-geography-contingency-volume-and-ground-risk-buffer-issue-17fcf7d91c3ff6e66b7b5ff0000aadb04.pdf?sfvrsn=433013f3_6
*/ 

// Gravity acceleration [m/s2]
const g = 9.81

// Maximum Operational Drone speed [m/s]
const Vd = 3

// Maximum UAS Characteristic Dimension [m]
const CD = 3

// Maximum wind speed [m/s]
const Vwind = 4

// GPS inacurracy distance [m]
const Sgps = 3

// Position Holding error [m]
const Spos = 3

// Map error [m]
const Sk = 1

// Reaction distance [m]
const Srz = Vd * 1

// Maximum pitch angle [deg]
const phi_max = 45 * (Math.PI / 180)

// Contingency maneuvers: Minium distance to stop hovering mode[m]
const Scm = 0.5*(Vd*Vd)/(g*Math.tan(phi_max))

// Lateral Contingency Volume distance [m]
const Scv = Sgps + Spos + Sk + Srz + Scm

// Altitude measurement error [m]
const Hbaro = 4

// Response height [m]
const Hrz = Vd*0.7*1

// Contingency maneuvers:
const Hcm = 0.5*(Vd*Vd)/g

// Lateral/Width Flight Geography distance [m] ----> TO BE DEFINED ----> PARAMETER
const Sfg = 20

// Height Flight Geography [m] ----> TO BE DEFINED ----> PARAMETER
const Hfg = 40

// Contingency Volume Height [m]
const Hcv = Hfg + Hbaro + Hrz + Hcm

// Lateral Ground Risk Buffer distance [m]
const approach = "PDRS-01" 

// Maximum Altitude above Ground Level (AGL) [m]
const AGL = Hcv

let Sgrb = 0
if (approach === "one-one-rule"){
    Sgrb = Hcv + 0.5*CD
}
else if (approach === "ballistic"){
    Sgrb = Vd*Math.sqrt(2*Hcv)/g + 0.5*CD
}
else if (approach === "PDRS-01"){
    // These are for MTOM greater than 10 kg
    if (AGL <= 10) {
        Sgrb = 10
    }
    else if ((AGL > 10) && (AGL <= 30)){
        Sgrb = 20
    }
    else if ((AGL > 30) && (AGL <= 60)){
        Sgrb = 30
    }
    else if ((AGL > 60) && (AGL <= 90)){
        Sgrb = 45
    }
    else if ((AGL > 90) && (AGL <= 120)){
        Sgrb = 60
    }
    else if ((AGL > 120) && (AGL <= 150)){
        Sgrb = 75
    }
    else {
        alert("AGL should be lower than 90")
    }
}

/* Visual Line Of Sight (VLoS)*/

// Max. Attitude Line Of Sight [m]: Maximum distance at which a remote pilot can detect the position and orientation of the UAS.
const ALoS = 327*CD + 20

/* Operations in VLoS required that the VLoS boundary is bigger than the contingecy volume (Sfg + Scv) */

export const DroneRegulationDefinitions = {
    AGL: AGL,
    Scv: Scv,
    Hcv: Hcv,
    Sgrb: Sgrb,
    ALoS: ALoS
}
