// Layered head-and-neck anatomy viewer (Z-Anatomy, CC BY-SA 4.0).
//
// Every tissue gets a procedural texture in the shader, so there are no image
// textures to license or ship: skin pores and blotching, elongated muscle
// fibres, porous bone, fat lobules, glandular lobules, moist mucosa. Cuts
// along the sagittal, coronal and axial planes are capped: a back face seen
// through a cut is drawn as the cut surface of that tissue, so the skin shows
// its epidermis, dermis and fat as bands.
//
// window.oc is the scripting surface the renderers use (see render.py).
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const KINDS = {
  epidermis: 1, dermis: 2, hypodermis: 3, muscle: 4, bone: 5, tooth: 6, cartilage: 7, artery: 8, vein: 9,
  nerve: 10, gland: 11, lymph: 12, mucosa: 13, brain: 14, eye: 15, sense: 16, duct: 17, fascia: 18,
  tongue: 19, gingiva: 20, tonsil: 21, oral: 22, lip: 23, hair: 24,
};
// base colour, cut colour, roughness, clearcoat
// Clinical-illustration palette, matched to the reels Ian approved: soft,
// desaturated tissue colours on pale grey. The first version used flesh tones
// and raw red muscle on a dark ground, and he called it terrifying (21 Oct).
const LOOK = {
  epidermis:  ["#c79479", "#efd9cf", 0.55, 0.6],  // clearcoat only where the lips are (scaled per pixel)
  dermis:     ["#efc9be", "#f0cdc2", 0.65, 0.0],
  hypodermis: ["#efd99a", "#f2e2ae", 0.35, 0.6],
  muscle:     ["#b95e55", "#d38a7e", 0.45, 0.4],
  bone:       ["#ede6d6", "#f1e9d6", 0.65, 0.05],
  tooth:      ["#eee4cf", "#f1eadb", 0.25, 0.8],
  cartilage:  ["#cdd9dc", "#d7e2e4", 0.45, 0.3],
  artery:     ["#c9554f", "#d8756f", 0.3, 0.75],
  vein:       ["#6676b4", "#8190c6", 0.3, 0.75],
  nerve:      ["#ebdca4", "#efe1a6", 0.36, 0.55],
  gland:      ["#ddb59b", "#e7c8ae", 0.45, 0.4],
  lymph:      ["#d6bc90", "#ddc7a0", 0.45, 0.4],
  mucosa:     ["#dd9a98", "#e8b1b1", 0.35, 0.8],
  brain:      ["#e8d6d0", "#e2cbc4", 0.6, 0.1],
  eye:        ["#ece7e0", "#e8e0d8", 0.5, 0.1],
  sense:      ["#e8d6bf", "#e8d6bf", 0.6, 0.1],
  duct:       ["#eadcc2", "#eadcc2", 0.5, 0.2],
  fascia:     ["#ece6de", "#efe9e1", 0.4, 0.45],
  // The mouth is where most oral cancers start, so these are true-to-life and
  // wet (full clearcoat, tight highlight) rather than illustrative (Ian, 22 Oct).
  // Colours matched to clinical photographs Ian sent: pale coral gum, pale
  // pink tongue with a whitish coat, salmon-pink cheek lining, ivory teeth.
  tongue:     ["#d6928e", "#d98a8a", 0.55, 1.0],
  gingiva:    ["#e39d95", "#e39a96", 0.5, 0.75],
  tonsil:     ["#c76a6d", "#cc7376", 0.45, 1.0],
  oral:       ["#d98b89", "#dc8f96", 0.4, 1.0],
  lip:        ["#bf6563", "#c87674", 0.45, 0.8],
  hair:       ["#2b1d16", "#2b1d16", 0.55, 0.3],   // eyelashes and eyebrows
};
const TEAL = new THREE.Color("#14a8ae");
const GHOSTED = new Set(["epidermis", "bone", "tooth", "cartilage"]);
const WET = new Set(["tongue", "gingiva", "tonsil", "oral", "lip"]);
// The open-mouth view: the soft tissues of the mouth and the teeth, with the skull as glass.
const MOUTH = new Set([...WET, "tooth"]);
// Generated linings that do not yet look like tissue; kept out of view until they do.
const JAWBONE = /^(Maxilla|Mandible|Palatine bone)/;   // solid in the mouth view, so tooth roots sit inside bone
const CRUDE = /^(Oropharynx|Nasopharynx|Laryngopharynx)/;   // the atlas's blocks for the throat spaces reach forward into the mouth

// Layers peel from the outside in. Depth n hides every class listed at < n.
const DEPTH_OF = { lip: 0, hair: 0, epidermis: 0, dermis: 0, hypodermis: 1, fascia: 1, muscle: 2, gland: 2, lymph: 2, bone: 3, tooth: 4, cartilage: 4 };

const NOISE = /* glsl */ `
vec3 ocHash3(vec3 p){ p = vec3(dot(p,vec3(127.1,311.7,74.7)), dot(p,vec3(269.5,183.3,246.1)), dot(p,vec3(113.5,271.9,124.6)));
  return fract(sin(p)*43758.5453123); }
float ocNoise(vec3 p){ vec3 i=floor(p), f=fract(p); vec3 u=f*f*(3.0-2.0*f);
  float n000=dot(ocHash3(i)-.5, f), n100=dot(ocHash3(i+vec3(1,0,0))-.5, f-vec3(1,0,0)),
        n010=dot(ocHash3(i+vec3(0,1,0))-.5, f-vec3(0,1,0)), n110=dot(ocHash3(i+vec3(1,1,0))-.5, f-vec3(1,1,0)),
        n001=dot(ocHash3(i+vec3(0,0,1))-.5, f-vec3(0,0,1)), n101=dot(ocHash3(i+vec3(1,0,1))-.5, f-vec3(1,0,1)),
        n011=dot(ocHash3(i+vec3(0,1,1))-.5, f-vec3(0,1,1)), n111=dot(ocHash3(i+vec3(1,1,1))-.5, f-vec3(1,1,1));
  return 2.2*mix(mix(mix(n000,n100,u.x),mix(n010,n110,u.x),u.y), mix(mix(n001,n101,u.x),mix(n011,n111,u.x),u.y), u.z); }
float ocFbm(vec3 p){ float a=.5, s=0.; for(int i=0;i<4;i++){ s+=a*ocNoise(p); p*=2.03; a*=.5; } return s; }
// distance to the nearest cell centre and to the cell edge
vec2 ocVoronoi(vec3 p){ vec3 i=floor(p), f=fract(p); float d1=8., d2=8.;
  for(int x=-1;x<=1;x++) for(int y=-1;y<=1;y++) for(int z=-1;z<=1;z++){ vec3 g=vec3(x,y,z); vec3 r=g+ocHash3(i+g)-f; float d=dot(r,r);
    if(d<d1){ d2=d1; d1=d; } else if(d<d2) d2=d; }
  return vec2(sqrt(d1), sqrt(d2)-sqrt(d1)); }
`;

// Albedo multiplier and bump height for each tissue, from object-space position
// (metres). `cut` is the pattern on a cut face rather than an outer surface.
// Every fine pattern fades out as it shrinks below a pixel or two (ocAA): left
// in, sub-millimetre noise turns into glittering grain at viewing distance,
// which is what made muscle and vessels read as painted concrete (Ian, 22 Oct).
const PATTERN = /* glsl */ `
float ocPx = 0.001;                            // metres per pixel here, set at the top of main()
float ocAA(float f){ return 1.0 - smoothstep(0.1, 0.45, ocPx*f); }
float ocN(vec3 p, float f){ return ocNoise(p*f)*ocAA(f); }
float ocF(vec3 p, float f){ float a=.5, s=0.; for(int i=0;i<4;i++){ s+=a*ocNoise(p*f)*ocAA(f); f*=2.03; a*=.5; } return s; }
void ocPattern(int k, vec3 p, vec3 fib, bool cut, out float shade, out float h, out vec3 tint){
  shade = 1.0; h = 0.0; tint = vec3(0.0);
  if(k==1){                                   // skin: soft mottling, warmer where blood is near the surface, pores up close
    float b = ocF(p, 40.0), m = ocF(p, 260.0), g = ocN(p, 2400.0);
    float pa = ocAA(1500.0*4.0); vec2 v = ocVoronoi(p*1500.0); float pore = smoothstep(0.09, 0.0, v.x)*pa;
    float ax = abs(p.x);
    float cheek = exp(-pow((ax - 0.042)/0.017, 2.0) - pow((p.y - 1.552)/0.018, 2.0)) * smoothstep(0.035, 0.07, p.z);
    float nose = exp(-pow(p.x/0.011, 2.0) - pow((p.y - 1.56)/0.014, 2.0)) * smoothstep(0.085, 0.105, p.z);
    float chin = exp(-pow(p.x/0.02, 2.0) - pow((p.y - 1.482)/0.013, 2.0)) * smoothstep(0.06, 0.09, p.z);
    float ear = smoothstep(0.064, 0.074, ax) * smoothstep(1.53, 1.56, p.y) * (1.0 - smoothstep(1.61, 1.64, p.y));
    float red = cheek*0.8 + nose*0.6 + chin*0.35 + ear*0.6;
    pore *= 1.0 - uTexOn; g *= 1.0 - uTexOn;          // the skin photo carries pores and fine lines when it is on
    shade = 1.0 + 0.04*b + 0.018*m - 0.06*pore;
    tint = vec3(0.045, -0.02, -0.02)*red + vec3(0.012, -0.002, -0.008)*b;
    h = -pore*0.18 + g*0.02;
    if(cut){ shade = 1.0; h = 0.0; tint = vec3(0.0); }
  } else if(k==2){
    shade = 0.95 + 0.05*ocF(p, 600.0); h = 0.0;
  } else if(k==3){                            // fat: glossy yellow lobules split by pale septa
    float f = cut ? 700.0 : 350.0, aa = ocAA(f*4.0); vec2 v = ocVoronoi(p*f); float sept = smoothstep(0.06, 0.0, v.y)*aa;
    shade = 0.96 + 0.06*(1.0-v.x)*aa - 0.06*sept; tint = vec3(0.05,0.035,0.05)*sept; h = ((1.0-v.x)*0.3 - sept*0.4)*aa;
  } else if(k==4){                            // muscle: long fascicles and finer fibres along the muscle's axis
    if(cut){ float aa = ocAA(2600.0*4.0); vec2 v = ocVoronoi(p*2600.0); float edge = smoothstep(0.08,0.0,v.y)*aa;
      shade = 0.93 + 0.07*(1.0-v.x)*aa - 0.14*edge; h = 0.0; }
    else {
      vec3 t1 = normalize(cross(fib, abs(fib.y) < 0.9 ? vec3(0,1,0) : vec3(1,0,0))), t2 = cross(fib, t1);
      vec3 q = vec3(dot(p,t1), dot(p,t2), dot(p,fib));
      float fa = ocNoise(vec3(q.xy*700.0, q.z*45.0))*ocAA(700.0);
      float fi = ocNoise(vec3(q.xy*2600.0, q.z*160.0))*ocAA(2600.0);
      float lo = ocF(p, 35.0);
      shade = 0.94 + 0.10*fa + 0.05*fi + 0.05*lo; h = fa*0.5 + fi*0.15; tint = vec3(0.03,-0.008,-0.008)*lo; }
  } else if(k==5){                            // bone: ivory, pitted; spongy where cut
    if(cut){ float aa = ocAA(900.0*3.0); vec2 v = ocVoronoi(p*900.0); float hole = smoothstep(0.32, 0.18, v.x)*aa;
      shade = 1.0 - 0.4*hole; tint = vec3(0.10,0.0,-0.02)*hole; h = 0.0; }
    else { float aa = ocAA(1600.0*4.0); vec2 v = ocVoronoi(p*1600.0); float pit = smoothstep(0.12,0.0,v.x)*aa; float b = ocF(p, 90.0);
      shade = 0.94 + 0.06*b - 0.06*pit; h = -pit*0.25 + b*0.15; tint = vec3(0.03,0.01,-0.03)*ocF(p, 30.0); }
  } else if(k==6){                            // enamel: ivory, faintly yellower in patches
    shade = 0.98 + 0.02*ocF(p, 300.0); tint = vec3(0.015,0.01,-0.025)*ocF(p, 60.0);
  } else if(k==7){ shade = 0.97 + 0.03*ocF(p, 400.0);
  } else if(k==8 || k==9){                    // vessels: smooth, wet walls
    float s = ocF(p, 160.0); shade = 0.97 + 0.04*s; h = s*0.15;
  } else if(k==10){ float s = ocF(p, 500.0); shade = 0.96 + 0.05*s; h = s*0.2;
  } else if(k==11 || k==12){                  // glands and nodes: lobulated
    float f = k==11 ? 500.0 : 900.0, aa = ocAA(f*4.0); vec2 v = ocVoronoi(p*f); float e = smoothstep(0.07,0.0,v.y)*aa;
    shade = 0.94 + 0.07*(1.0-v.x)*aa - 0.1*e; h = ((1.0-v.x)*0.6 - e)*aa;
  } else if(k==13){ float s = ocF(p, 500.0); float pa = ocAA(1800.0*5.0); float papil = smoothstep(0.12,0.0,ocVoronoi(p*1800.0).x)*pa;
    shade = 0.94 + 0.06*s + 0.05*papil; h = s*0.3 + papil*0.4;
  } else if(k==14){ float s = ocF(p, 200.0); shade = cut ? 1.0 : 0.93 + 0.07*s; h = s*0.5;
  } else if(k==19){                           // tongue: pale velvety coat, red dots, a midline groove, veined underside
    vec3 wn = normalize(cross(dFdx(vPosT), dFdy(vPosT))); if(dot(wn, cameraPosition - vPosO) < 0.0) wn = -wn;
    float d = smoothstep(0.1, 0.6, wn.y), under = smoothstep(-0.55, -0.85, wn.y);
    float fil = ocN(p, 4200.0)*0.5;
    float fa = ocAA(420.0*7.0); vec2 fv = ocVoronoi(p*420.0); float fung = smoothstep(0.13, 0.07, fv.x)*step(0.35, fract(fv.x*91.7 + p.x*13.0))*fa;
    float groove = exp(-pow(p.x/0.0016, 2.0)) * d;
    float vein = (1.0 - smoothstep(0.0, 0.05, abs(ocNoise(p*vec3(260.0, 260.0, 110.0)))))*ocAA(260.0*20.0);
    shade = 0.97 + 0.04*ocF(p, 300.0);
    tint = vec3(0.07, 0.07, 0.07)*d*(0.6 + fil) + vec3(0.10, -0.06, -0.05)*fung*d - vec3(0.06, 0.06, 0.04)*groove + vec3(-0.10, -0.06, 0.05)*vein*under;
    h = d*(fil*0.4 + fung*0.6) - groove*1.4 + under*vein*0.3;
  } else if(k==20){                           // gum: matte-ish coral pink, stippled like orange peel
    float aa = ocAA(2200.0*4.0); vec2 vg = ocVoronoi(p*2200.0); float pit = smoothstep(0.12, 0.0, vg.x)*aa;
    shade = 0.98 + 0.03*ocF(p, 120.0) - 0.03*pit; h = -pit*0.3;
  } else if(k==21){                           // tonsil: lobulated, pitted with crypts
    float aa = ocAA(380.0*5.0); vec2 cr = ocVoronoi(p*380.0); float hole = smoothstep(0.16, 0.06, cr.x)*aa, lob = (1.0 - cr.x)*aa;
    hole *= 1.0 - uTexOn;                              // the tonsil photo has real crypts
    shade = 0.93 + 0.08*lob - 0.3*hole; tint = vec3(-0.05, -0.06, -0.04)*hole; h = lob*0.5 - hole*1.2;
  } else if(k==22){                           // lining mucosa: smooth, translucent, a fine net of vessels; ridged at the front of the hard palate
    float va = ocAA(300.0*18.0);
    float ves = (1.0 - smoothstep(0.0, 0.02, abs(ocNoise(p*300.0 + 4.0))))*va + 0.5*(1.0 - smoothstep(0.0, 0.03, abs(ocNoise(p*700.0))))*ocAA(700.0*18.0);
    shade = 0.98 + 0.03*ocF(p, 150.0); tint = vec3(0.035, -0.025, -0.02)*ves*0.6; h = 0.0;
    float rug = step(1.533, p.y)*step(p.y, 1.56)*step(0.055, p.z)*step(p.z, 0.086)*step(abs(p.x), 0.019);
    h += rug * sin(p.z*1500.0 + ocNoise(p*180.0)*3.0) * 0.6 * ocAA(240.0*4.0);
  } else if(k==23){                           // lip: fine vertical creases
    float cr = ocNoise(vec3(p.x*2600.0, p.y*260.0, p.z*2600.0))*ocAA(2600.0);
    shade = 0.95 + 0.05*cr; h = cr*0.5;
  } else if(k==15 && uIris.w > 0.0){           // iris: radial fibres, a paler ring round the pupil, a dark outer rim
    vec3 d = p - uIris.xyz, pl = d - uIrisN*dot(d, uIrisN); float r = length(pl)/uIris.w;
    vec3 e1 = normalize(cross(uIrisN, vec3(0.0, 1.0, 0.0))), e2 = cross(uIrisN, e1); float ang = atan(dot(pl, e2), dot(pl, e1));
    float fib = ocNoise(vec3(cos(ang)*7.0, sin(ang)*7.0, r*2.5))*0.5 + 0.5, fib2 = ocNoise(vec3(cos(ang)*22.0, sin(ang)*22.0, r*5.0 + 3.0))*0.5 + 0.5;
    float collar = exp(-pow((r - 0.42)/0.08, 2.0)), limbal = smoothstep(0.72, 0.98, r);
    shade = 0.7 + 0.35*fib + 0.2*fib2 - 0.55*limbal;
    tint = vec3(0.16, 0.11, 0.03)*collar;
  } else { shade = 0.97 + 0.03*ocF(p, 300.0); }
}
`;

function makeMaterial(cls, fib) {
  const [base, cut, rough, coat] = LOOK[cls] || LOOK.sense;
  const m = new THREE.MeshPhysicalMaterial({
    color: base, roughness: rough, metalness: 0, clearcoat: coat, clearcoatRoughness: WET.has(cls) || cls === "tooth" ? 0.05 : { muscle: 0.25, artery: 0.12, vein: 0.12, nerve: 0.2, hypodermis: 0.18, mucosa: 0.1 }[cls] ?? 0.3,
    side: THREE.DoubleSide, sheen: cls === "muscle" ? 0.35 : cls === "epidermis" ? 0.18 : 0, sheenColor: new THREE.Color(cls === "epidermis" ? "#ffe4d8" : "#ffd0c4"), sheenRoughness: cls === "epidermis" ? 0.35 : 0.5,
  });
  const u = m.userData.u = {
    uKind: { value: KINDS[cls] || 16 }, uCut: { value: new THREE.Color(cut) }, uFib: { value: fib || new THREE.Vector3(0, 1, 0) },
    uHL: { value: 0 }, uGhost: { value: 0 }, uRig: { value: 0 }, uGlint: { value: 1 }, uIris: { value: new THREE.Vector4(0, 0, 0, 0) }, uIrisN: { value: new THREE.Vector3(0, 0, 1) }, uTeal: { value: TEAL }, uPlanes: SHARED.planes, uPlaneOn: SHARED.planeOn, uCave: SHARED.cave, uLipA: SHARED.lipA, uLipB: SHARED.lipB,
    uBump: { value: { epidermis: 0.00006, muscle: 0.00002, bone: 0.0005, hypodermis: 0.0003, artery: 0.0002, vein: 0.0002, nerve: 0.0002,
      tongue: 0.00006, gingiva: 0.00004, tonsil: 0.0001, oral: 0.00003, lip: 0.00006, tooth: 0.00005, gland: 0.0003, lymph: 0.0003, hair: 0 }[cls] ?? 0.00015 }, uWrap: { value: cls === "mucosa" || WET.has(cls) ? 1 : cls === "muscle" ? 0.4 : cls === "epidermis" ? 0.45 : 0 }, uNoFront: { value: 0 }, uForceCut: { value: 0 },
    uLipOn: { value: cls === "epidermis" ? 1 : 0 }, uLip: { value: cls === "epidermis" ? tex("lips", true) : BLANK },
    uTexOn: { value: PHOTO[cls] ? 1 : 0 }, uTexScale: { value: PHOTO[cls] ? PHOTO[cls][2] : 1 },
    uTex: { value: PHOTO[cls] ? tex(PHOTO[cls][0], true) : BLANK }, uHgt: { value: PHOTO[cls] ? tex(PHOTO[cls][0] + "_h", false) : BLANK },
    uTex2: { value: PHOTO[cls] && PHOTO[cls][1] ? tex(PHOTO[cls][1], true) : BLANK }, uHgt2: { value: PHOTO[cls] && PHOTO[cls][1] ? tex(PHOTO[cls][1] + "_h", false) : BLANK },
  };
  m.customProgramCacheKey = () => "oc-tissue";
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, u);
    sh.vertexShader = sh.vertexShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vPosO; varying vec3 vPosT; varying vec3 vNrmW; attribute vec3 ocRest; uniform float uRig;")
      .replace("#include <beginnormal_vertex>", "#include <beginnormal_vertex>\nvNrmW = normalize(mat3(modelMatrix) * objectNormal);")
      .replace("#include <begin_vertex>", "#include <begin_vertex>\nvPosO = (modelMatrix * vec4(position, 1.0)).xyz; vPosT = uRig > 0.5 ? ocRest : vPosO;");
    sh.fragmentShader = sh.fragmentShader
      .replace("#include <common>", `#include <common>
// vPosO is where the surface is now; vPosT is where it sits with the mouth closed, so patterns
// and photos stay on the tissue as the jaw opens rather than sliding over it.
varying vec3 vPosO; varying vec3 vPosT; varying vec3 vNrmW;
uniform int uKind; uniform float uRig; uniform float uGlint; uniform vec4 uIris; uniform vec3 uIrisN; uniform vec3 uCut; uniform vec3 uFib; uniform float uHL; uniform float uGhost; uniform vec3 uTeal;
uniform vec4 uPlanes[3]; uniform float uPlaneOn[3]; uniform float uBump; uniform float uWrap; uniform float uNoFront; uniform float uForceCut;
uniform float uLipOn; uniform sampler2D uLip; uniform float uCave; uniform vec4 uLipA; uniform vec4 uLipB;
uniform float uTexOn; uniform float uTexScale; uniform sampler2D uTex; uniform sampler2D uHgt; uniform sampler2D uTex2; uniform sampler2D uHgt2;
// triplanar: project the tile along each axis and blend by how the surface faces (v runs up the body on the side and front projections)
vec4 ocTri(sampler2D t, vec3 q, vec3 w){ return texture2D(t, q.zy)*w.x + texture2D(t, q.xz)*w.y + texture2D(t, q.xy)*w.z; }
vec4 ocTriB(sampler2D t, vec3 q, vec3 w, float b){ return texture2D(t, q.zy, b)*w.x + texture2D(t, q.xz, b)*w.y + texture2D(t, q.xy, b)*w.z; }
${NOISE}
${PATTERN}`)
      .replace("void main() {", `void main() {
  // Under intact epidermis, the dermis and fat are only ever seen where cut
  // (a back face); a front face showing means it poked through the skin.
  ocPx = length(fwidth(vPosO)) * 0.7;
  float ocH = 0.0; float ocCoat = 1.0; vec3 ocGlint = vec3(0.0); bool ocCap = false; vec3 ocCapN = vec3(0.0); float ocNear = 1e9;
  for(int i=0;i<3;i++){ if(uPlaneOn[i] > 0.5){ float d = abs(dot(uPlanes[i].xyz, vPosO) + uPlanes[i].w);
    if(d < ocNear){ ocNear = d; ocCapN = uPlanes[i].xyz; } } }
  // Under intact epidermis the dermis and fat only ever show as a band at a
  // cut. Anything else of them on screen is a fold where they cross the
  // surface (under the nose, inside the ear), so draw them only near a cut.
  // Drawn as skin rather than dropped: where the atlas skin has a fold or seam,
  // dropping them would show the muscle behind.
  bool ocAsSkin = uNoFront > 0.5 && (gl_FrontFacing || ocNear > 0.012);
  // The dermis and fat only poke through the epidermis at folds (they crumpled the skin under the
  // nose), so away from a cut they are not drawn. The skin's outer surface faces out (oriented in
  // export_head.py), so a back face of the epidermis away from a cut is its inside, seen into a
  // nostril, an ear canal or the parted lips: drawn as shadow.
  if(ocAsSkin && ocNear > 0.012) discard;
  bool ocInside = uKind == 1 && uForceCut < 0.5 && !gl_FrontFacing && ocNear > 0.012;
  if(!gl_FrontFacing && !ocAsSkin) ocCap = ocNear < 1e8;   // a back face seen through a cut is the cut surface
  bool ocFlat = ocCap;                         // lit as the cut plane
  if(uForceCut > 0.5) ocCap = true;            // a face that is a cut by construction (the tissue block's sides)`)
      .replace("#include <color_fragment>", `#include <color_fragment>
  { float sh_, h_; vec3 t_; ocPattern(ocAsSkin ? 1 : uKind, vPosT, uFib, ocCap, sh_, h_, t_);
    vec3 base = ocAsSkin ? vec3(0.571, 0.296, 0.195) : ocCap ? uCut : diffuseColor.rgb;
    diffuseColor.rgb = clamp(base*sh_ + t_, 0.0, 1.0); ocH = h_;
    if(ocInside){ diffuseColor.rgb *= vec3(0.32, 0.22, 0.2); ocH = 0.0; }
    if(uTexOn > 0.5 && !ocCap && !ocAsSkin){
      // the atlas's normals are not reliably outward: use the side facing the camera
      vec3 wn = normalize(vNrmW); if(dot(wn, cameraPosition - vPosO) < 0.0) wn = -wn;
      vec3 bw = pow(abs(wn), vec3(4.0)); bw /= (bw.x + bw.y + bw.z);
      vec3 q = vPosT / uTexScale;
      // Ian's photos give the fine variation and relief (red dots, stipple, folds);
      // the colour comes from the palette, so each photo is divided by its own average.
      vec3 ph = ocTri(uTex, q, bw).rgb, pm = ocTriB(uTex, q, bw, 14.0).rgb;
      float hh = ocTri(uHgt, q, bw).r, hm = ocTriB(uHgt, q, bw, 14.0).r;
      if(uKind == 19){                          // tongue: the underside photo where the surface faces down
        // which side faces down, from the surface itself (the atlas's stored normals point every which way)
        vec3 fn = normalize(cross(dFdx(vPosO), dFdy(vPosO))); if(dot(fn, cameraPosition - vPosO) < 0.0) fn = -fn;
        float under = smoothstep(-0.55, -0.85, fn.y);   // only what clearly faces down
        ph = mix(ph, ocTri(uTex2, q, bw).rgb, under); pm = mix(pm, ocTriB(uTex2, q, bw, 14.0).rgb, under);
        hh = mix(hh, ocTri(uHgt2, q, bw).r, under); hm = mix(hm, ocTriB(uHgt2, q, bw, 14.0).r, under);
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.62, 0.36, 0.40), under*0.6);   // the underside is redder, bluish with veins
        ocCoat = mix(0.35, 1.0, under);          // the coated top is velvety with scattered glints; the underside is glassy
      }
      // (the cheek photo has bright saliva highlights baked in: clamped, or they print as white blotches)
      // (the cheek and throat photos are flat-lit since 22 Oct, so they no longer need muting)
      float dLo = uKind == 1 ? 0.6 : uKind == 22 ? 0.5 : 0.2, dHi = uKind == 1 ? 1.5 : uKind == 22 ? 1.6 : 3.0;
      float dK = uKind == 19 ? 0.6 : uKind == 21 ? 0.75 : uKind == 1 ? 0.55 : 0.5;
      vec3 det = pow(clamp(ph / max(pm, vec3(0.03)), dLo, dHi), vec3(dK));
      diffuseColor.rgb = clamp(diffuseColor.rgb * det, 0.0, 1.0);
      ocH += (hh - hm) * (uKind == 1 ? 0.2 : 0.8) * ocAA(1.0 / (uTexScale * 0.004));   // relief only up close: further out it turns to grain
      if(uKind == 20) ocCoat = 0.55;            // gum: keratinised, a softer shine than the lining
    }
    if(uLipOn > 0.5){
      // The red of the lip (vermilion), up and down from the line where the lips meet, as Ian placed it with the
      // lip tuner (22 Oct). The upper border tapers toward the corners with a small cupid's bow, the lower one
      // is rounder, and both close in at the corners.
      // (the numbers live in SHARED.lipA/lipB so they can be tuned by eye: oc.lips())
      float ax = abs(vPosT.x), dy = vPosT.y - uLipA.x, lw = uLipA.w;
      float hu = uLipA.y*max(0.0, 1.0 - pow(ax/lw, 1.8)) + uLipB.x*(0.0008*exp(-pow((ax - 0.22*lw)/0.003, 2.0)) - 0.0012*exp(-pow(ax/0.0025, 2.0)));
      float hl = uLipA.z*sqrt(max(0.0, 1.0 - pow(ax/(0.96*lw), 2.0)));
      float lip = (dy > 0.0 ? 1.0 - smoothstep(hu - 0.0012, hu, dy) : 1.0 - smoothstep(hl - 0.0015, hl, -dy))
        * step(ax, lw) * smoothstep(0.072, 0.08, vPosT.z) * (ocCap || ocAsSkin ? 0.0 : 1.0);
      vec3 wl = abs(normalize(vNrmW)); wl = pow(wl, vec3(4.0)); wl /= (wl.x + wl.y + wl.z);
      vec3 la = ocTri(uLip, vPosT / 0.015, wl).rgb;
      diffuseColor.rgb = mix(diffuseColor.rgb, la, lip*0.9); ocCoat = lip;
      if(uLipB.z > 0.5){   // where the mouth would open, drawn across the front of the face while tuning
        float g = (1.0 - smoothstep(0.0002, 0.0004, abs(vPosT.y - uLipB.y))) * step(ax, lw + 0.004) * smoothstep(0.06, 0.07, vPosT.z);
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.08, 0.66, 0.68), g);
      }
    }
    // saliva: the clear coat ripples, so a wet surface breaks the light into many small glints
    if(uWrap > 0.9 && !ocCap){ vec3 gq = vPosT*800.0; ocGlint = vec3(ocNoise(gq), ocNoise(gq + 17.3), ocNoise(gq + 31.7))*0.16*uGlint*ocAA(800.0*2.0); }
    diffuseColor.rgb = mix(diffuseColor.rgb, uTeal*(0.75 + 0.25*sh_), 0.82*uHL); }`)
      .replace("#include <clearcoat_normal_fragment_maps>", `#include <clearcoat_normal_fragment_maps>
  #ifdef USE_CLEARCOAT
    // three starts the coat from the unflipped normal; use the camera-facing one, plus the saliva ripple
    clearcoatNormal = normalize(normal + (viewMatrix * vec4(ocGlint, 0.0)).xyz);
  #endif`)
      .replace("#include <lights_physical_fragment>", `#include <lights_physical_fragment>
  #ifdef USE_CLEARCOAT
    material.clearcoat *= ocCoat;
  #endif`)
      .replace("#include <normal_fragment_maps>", `#include <normal_fragment_maps>
  if(ocFlat){ normal = normalize((viewMatrix * vec4(-ocCapN, 0.0)).xyz); if(normal.z < 0.0) normal = -normal; }
  // The atlas's winding is not consistent, so a surface seen from its "back"
  // is usually just wound the other way: light whichever side faces the camera.
  if(!ocFlat && dot(normal, vViewPosition) < 0.0) normal = -normal;
  if(!ocFlat && uBump > 0.0){
    vec3 sX = dFdx(-vViewPosition), sY = dFdy(-vViewPosition); vec3 R1 = cross(sY, normal), R2 = cross(normal, sX);
    float det = dot(sX, R1); vec2 dH = vec2(dFdx(ocH), dFdy(ocH)) * uBump * 40.0;
    vec3 g = sign(det) * (dH.x*R1 + dH.y*R2); normal = normalize(abs(det)*normal - g); }`)
      .replace("#include <dithering_fragment>", `#include <dithering_fragment>
  if(uWrap > 0.0 && !ocCap){                 // a little light bleeding through skin and mucosa
    float rim = pow(1.0 - abs(dot(normalize(normal), normalize(vViewPosition))), 3.0);
    gl_FragColor.rgb += vec3(0.20,0.05,0.03)*rim*0.6*uWrap; }
  if(uCave > 0.5 && uWrap > 0.9 || uCave > 0.5 && uKind == 6){   // inside the mouth: less light reaches the back
    float back = smoothstep(0.075, 0.015, vPosO.z);
    gl_FragColor.rgb *= mix(1.0, 0.62, back); gl_FragColor.rgb = mix(gl_FragColor.rgb, gl_FragColor.rgb*vec3(1.05, 0.9, 0.9), back); }
  if(uHL > 0.0) gl_FragColor.rgb += uTeal*0.10*uHL;
  if(uGhost > 0.0){                          // see-through: glassy at the silhouette, clear face-on
    float f = pow(1.0 - abs(dot(normalize(normal), normalize(vViewPosition))), 2.2);
    gl_FragColor = vec4(mix(vec3(0.28,0.38,0.41), gl_FragColor.rgb, 0.15), mix(0.012, 0.21, f) * uGhost); }`);
  };
  return m;
}

// Photo textures for the mouth (made by Ian with an image model, 22 Oct), made
// seamless in textures/; each has a matching height map for the relief.
const TEX_BASE = window.TEX_BASE || "textures/";
const texLoader = new THREE.TextureLoader();
const BLANK = new THREE.DataTexture(new Uint8Array([255, 255, 255, 255]), 1, 1); BLANK.needsUpdate = true;
const texCache = {};
function tex(name, srgb) {
  const key = name + (srgb ? ":c" : ":h");
  if (!texCache[key]) {
    const t = texLoader.load(TEX_BASE + name + ".jpg");
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    texCache[key] = t;
  }
  return texCache[key];
}
// which texture each mouth tissue wears, and how many metres one tile covers
// (tonsil, throat, skin, cheek and the second lips were made with Gemini, 22 Oct)
const PHOTO = { tongue: ["tongue_top", "tongue_under", 0.02], gingiva: ["gums", null, 0.015], lip: ["lips", null, 0.015],
                oral: ["cheek", null, 0.02], tonsil: ["tonsil", null, 0.014], epidermis: ["skin", null, 0.03] };
// the throat's linings wear the throat photo rather than the cheek's
const THROAT = /^(Posterior pharyngeal wall|Palatoglossal arch|Palatopharyngeal arch|Soft palate mucosa|Uvula of palate)/;

// Where the lips meet (m): placed by Ian with the lip tuner, 22 Oct (STOMION in export_head.py, which parts the skin here)
const LIP_LINE = 1.530;

const SHARED = {
  planes: { value: [new THREE.Vector4(), new THREE.Vector4(), new THREE.Vector4()] },
  planeOn: { value: [0, 0, 0] },
  cave: { value: 0 },                          // 1 in the open-mouth view
  // the lips' colour: where the lips meet (y), how far it reaches up and down from there, half its width (m)
  lipA: { value: new THREE.Vector4(LIP_LINE, 0.0095, 0.0125, 0.031) },   // Ian's values from the lip tuner, 22 Oct
  // the cupid's bow (1 = as measured), and a guide line across the face at y when the third value is 1
  lipB: { value: new THREE.Vector4(1, LIP_LINE, 0, 0) },
};

// ---- scene -------------------------------------------------------------------
const stage = document.getElementById("stage");
let W = stage.clientWidth || window.innerWidth, H = stage.clientHeight || window.innerHeight;
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
renderer.setSize(W, H);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.localClippingEnabled = true;
stage.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.95;
const key = new THREE.DirectionalLight("#fff8f0", 1.5); key.position.set(0.5, 0.8, 1.0); scene.add(key);
const fill = new THREE.DirectionalLight("#eef4ff", 0.8); fill.position.set(-1, 0.2, 0.6); scene.add(fill);
const rim = new THREE.DirectionalLight("#ffffff", 0.7); rim.position.set(-0.3, 0.6, -1.0); scene.add(rim);
// An exam light that follows the camera, so wet surfaces catch a highlight from wherever you look.
const exam = new THREE.DirectionalLight("#fffaf2", 0.5); scene.add(exam); scene.add(exam.target);
// In the mouth view the room light drops and the exam light carries the scene, as with a penlight.
function aimExam() {
  const mouth = state.mode === "mouth";
  exam.position.copy(camera.position); exam.target.position.copy(controls.target); exam.intensity = mouth ? 1.5 : 0.5;
  scene.environmentIntensity = mouth ? 0.5 : 0.95; key.intensity = mouth ? 0.9 : 1.5; fill.intensity = mouth ? 0.4 : 0.8;
  renderer.toneMappingExposure = mouth ? 0.9 : 1.0; SHARED.cave.value = mouth ? 1 : 0;
}
const camera = new THREE.PerspectiveCamera(30, W / H, 0.005, 20);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.minDistance = 0.02; controls.maxDistance = 1.5;
new ResizeObserver(() => {
  W = stage.clientWidth; H = stage.clientHeight; if (!W || !H) return;
  renderer.setSize(W, H); camera.aspect = W / H; camera.updateProjectionMatrix();
}).observe(stage);

const meshes = [], byName = new Map(), CLIP = [new THREE.Plane(), new THREE.Plane(), new THREE.Plane()];
let center = new THREE.Vector3(), size = 0.3, ready = false;
const state = { mode: "full", depth: 0, planes: [null, null, null], hl: new Set(), labels: [] };

function principalAxis(geo, mw) {
  const p = geo.attributes.position, n = p.count, step = Math.max(1, Math.floor(n / 400)), c = new THREE.Vector3(), v = new THREE.Vector3();
  let k = 0; for (let i = 0; i < n; i += step) { c.add(v.fromBufferAttribute(p, i).applyMatrix4(mw)); k++; } c.divideScalar(k);
  const m = [0, 0, 0, 0, 0, 0];
  for (let i = 0; i < n; i += step) { v.fromBufferAttribute(p, i).applyMatrix4(mw).sub(c); m[0] += v.x * v.x; m[1] += v.y * v.y; m[2] += v.z * v.z; m[3] += v.x * v.y; m[4] += v.x * v.z; m[5] += v.y * v.z; }
  let a = new THREE.Vector3(1, 1, 1).normalize();
  for (let it = 0; it < 12; it++) a = new THREE.Vector3(m[0] * a.x + m[3] * a.y + m[4] * a.z, m[3] * a.x + m[1] * a.y + m[5] * a.z, m[4] * a.x + m[5] * a.y + m[2] * a.z).normalize();
  return a;
}

const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
function onModel(gltf) {
  document.body.dataset.progress = "100";
  const root = gltf.scene; root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isMesh) return;
    const node = o.userData.cls ? o : o.parent;          // extras live on the node
    const cls = node.userData.cls || "sense";
    const name = (node.userData.label || node.name || o.name).replace(/\.0\d\d$/, "");
    o.material = makeMaterial(cls, cls === "muscle" ? principalAxis(o.geometry, o.matrixWorld) : null);
    o.material.clippingPlanes = [];
    // generated mouth linings are single sheets drawn from the lining side only (see export_head.py)
    if (/^(Buccal mucosa|Upper labial mucosa|Lower labial mucosa|Floor of mouth mucosa|Upper lip|Lower lip)$/.test(name.replace(/\.(l|r)$/, ""))) o.material.side = THREE.FrontSide;
    // Eyes in soft natural colours to match the skin: blank sculpted eyes on a skin-toned face read as a statue.
    if (THROAT.test(name)) { const u = o.material.userData.u; u.uTex.value = tex("throat", true); u.uHgt.value = tex("throat_h", false); u.uTexScale.value = 0.025; u.uGlint.value = 0.35; }   // seen face-on in the exam light: fewer glints, or it frosts
    if (/^Iris/.test(name)) {
      o.material.color.set(window.OC_IRIS || "#6b5644");
      const b = new THREE.Box3().setFromObject(o), c = b.getCenter(new THREE.Vector3()), sz = b.getSize(new THREE.Vector3());
      o.material.userData.u.uIris.value.set(c.x, c.y, c.z, Math.max(sz.x, sz.y) / 2);
      o.material.userData.u.uIrisN.value.set(c.x * 0.6, 0, 1).normalize();   // eyes look forward and a little outward
    }
    if (/^(Vitreous body|Posterior segment|Retina)/.test(name)) o.material.color.set("#2a2220");   // the pupil reads dark
    if (/^Sclera/.test(name)) { o.material.color.set("#efe9e2"); o.material.roughness = 0.3; o.material.clearcoat = 1; o.material.clearcoatRoughness = 0.05; }
    if (/^(Cornea|Anterior chamber|Lens)/.test(name)) { o.material.transparent = true; o.material.opacity = 0.12; o.userData.glass = true; }
    // The cornea adds only its reflection (additive, black body), so the iris shows through clear and the
    // eye catches a wet glint; the lens and the chamber behind it are not drawn (they milked the iris over).
    if (/^Cornea/.test(name)) Object.assign(o.material, { blending: THREE.AdditiveBlending, opacity: 1, roughness: 0.03, clearcoat: 1,
      clearcoatRoughness: 0.0, envMapIntensity: 0.0, depthWrite: false, color: new THREE.Color("#000000") });   // lights only: the room reflection washed the iris out
    if (/^(Lens|Anterior chamber|Anterior segment)/.test(name)) { o.material.opacity = 0; o.material.colorWrite = false; o.userData.glass = true; }
    o.userData.cls = cls; o.userData.name = name; o.renderOrder = cls === "epidermis" ? 2 : 0;
    meshes.push(o);
    if (!byName.has(name)) byName.set(name, []); byName.get(name).push(o);
  });
  scene.add(root);
  block = buildBlock(); block.position.set(0, 0, 0); scene.add(block);
  const box = new THREE.Box3().setFromObject(root); box.getCenter(center); size = box.getSize(new THREE.Vector3()).length();
  controls.target.copy(center); view(25, 8, 1.9);
  rigJaw();
  apply(); ready = true;
  document.body.dataset.ready = "1";
  if (window.onOcReady) window.onOcReady();
}
const onFail = (err) => { document.body.dataset.error = String(err && err.message || err); };
if (window.MODEL_PARTS) {
  // Published artifacts do not serve .glb, so the model ships as base64 text in parts.
  let done = 0;
  Promise.all(window.MODEL_PARTS.map((u) => fetch(u).then((r) => { if (!r.ok) throw new Error(u + " " + r.status); return r.text(); })
    .then((t) => { done++; document.body.dataset.progress = String(Math.round(90 * done / window.MODEL_PARTS.length)); return t; })))
    .then((parts) => {
      const bin = atob(parts.join("").replace(/\s+/g, "")), buf = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      loader.parse(buf.buffer, "", onModel, onFail);
    }).catch(onFail);
} else {
  loader.load(window.MODEL_URL || "head.glb", onModel,
    (e) => { if (e.total) document.body.dataset.progress = String(Math.round(100 * e.loaded / e.total)); }, onFail);
}

// ---- tissue block ----------------------------------------------------------------
// The skin's layers are a millimetre or two thick, too thin to read on the
// head, so they get the textbook treatment: a stepped block of tissue, each
// layer cut back to show the one beneath, with a vessel pair and a nerve
// running through the fat. Thicknesses are proportional except the
// epidermis, drawn about five times thicker than life so it can be seen.
function buildBlock() {
  const g = new THREE.Group(); g.visible = false;
  const Wd = 0.034, D = 0.022, step = 0.0045;
  const layers = [["bone", "Bone (block)", 0.004], ["muscle", "Muscle (block)", 0.005], ["hypodermis", "Hypodermis (block)", 0.0045],
                  ["dermis", "Dermis (block)", 0.0018], ["epidermis", "Epidermis (block)", 0.0005]];
  let y = 0;
  layers.forEach(([cls, name, th], i) => {
    const w = Wd - i * step, geo = new THREE.BoxGeometry(w, th, D, 24, 2, 16);
    const top = makeMaterial(cls, cls === "muscle" ? new THREE.Vector3(1, 0, 0) : null), side = makeMaterial(cls, new THREE.Vector3(1, 0, 0));
    side.userData.u.uForceCut.value = 1;
    const mats = [side, side, top, side, side, side];          // +x -x +y -y +z -z
    const m = new THREE.Mesh(geo, mats); m.position.set(-Wd / 2 + w / 2, y + th / 2, 0);
    m.userData = { cls, name, block: true }; g.add(m); y += th;
  });
  const tube = (cls, name, r, x, yy) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, D * 1.002, 24, 1), [makeMaterial(cls), makeMaterial(cls), makeMaterial(cls)]);
    m.material[1].userData.u.uForceCut.value = 1; m.material[2].userData.u.uForceCut.value = 1;
    m.rotation.x = Math.PI / 2; m.position.set(x, yy, 0); m.userData = { cls, name, block: true }; g.add(m);
  };
  const fatY = 0.004 + 0.005 + 0.00225;
  tube("artery", "Artery (block)", 0.0009, -0.004, fatY); tube("vein", "Vein (block)", 0.0012, -0.0005, fatY + 0.0003); tube("nerve", "Nerve (block)", 0.0006, 0.0028, fatY - 0.0004);
  g.traverse((o) => { if (o.isMesh) { meshes.push(o); const n = o.userData.name; if (!byName.has(n)) byName.set(n, []); byName.get(n).push(o);
    (Array.isArray(o.material) ? o.material : [o.material]).forEach((mm) => { mm.clippingPlanes = []; }); } });
  return g;
}
let block = null;

// ---- the jaw ---------------------------------------------------------------------
// The open-mouth view swings the lower jaw about the jaw joints. Bone, lower
// teeth, lower gum, lower lip, inner lower lip and the floor of the mouth turn
// with it; the tongue and cheek linings bend, their front and lower parts
// following the jaw more than the back and upper parts.
const JAW_MAX = 0.42;                          // about 24 degrees, a wide but normal opening
const pivot = new THREE.Vector3();
const rigged = [];
const RIGID = /^(Mandible|Lower (?!lip|labial|gingiva).*(incisor|canine|premolar|molar).*|Lower gingiva|Lower lip|Lower labial mucosa|Floor of mouth mucosa|Sublingual gland.*)$/;
// When the mouth opens the lips part: the upper lip lifts off the incisors and the lower lip drops
// away from the lower ones, most at the lip edge and not at all at the fold where lip meets gum.
const LIFT = {
  "Upper lip": [new THREE.Vector3(0, 0.0075, 0.0015), (q) => THREE.MathUtils.smoothstep(-q.y, -1.552, -1.522)],
  "Upper labial mucosa": [new THREE.Vector3(0, 0.0075, 0.0015), (q) => THREE.MathUtils.smoothstep(-q.y, -1.552, -1.522)],
  "Lower lip": [new THREE.Vector3(0, -0.004, 0.001), (q) => THREE.MathUtils.smoothstep(q.y, 1.509, 1.517)],
  "Lower labial mucosa": [new THREE.Vector3(0, -0.004, 0.001), (q) => THREE.MathUtils.smoothstep(q.y, 1.509, 1.517)],
};
// The face moves with the jaw: everything below the line where the lips meet turns with it (chin,
// lower lip, the skin over the jaw), fading out behind the angle of the jaw, down the neck, and
// across a band that widens past the corners of the mouth so the cheeks stretch rather than tear.
// The skin is parted along that line in export_head.py.
function skinJaw(q) {
  const ax = Math.abs(q.x), band = 0.00003 + 0.5 * Math.max(0, ax - 0.024);
  const yc = LIP_LINE;                            // the lips' cut edges sit 0.05 mm either side of this
  const below = THREE.MathUtils.smoothstep(-q.y, -(yc + band), -(yc - band));
  // (the fades are long: shorter ones folded the skin over at the angle of the jaw, which showed as dark specks)
  return below * THREE.MathUtils.smoothstep(q.z, -0.045, 0.05) * THREE.MathUtils.smoothstep(q.y, 1.40, 1.485);
}
// and the upper lip lifts a little off the teeth, most at its edge and the middle
// (since the lip line moved up to where Ian placed it, the upper teeth end 4.5 mm below it, so only a small lift is needed)
const SKIN_LIFT = [new THREE.Vector3(0, 0.003, 0.001), (q) => (1 - skinJaw(q)) * (1 - THREE.MathUtils.smoothstep(q.y, LIP_LINE + 0.002, LIP_LINE + 0.022))
  * (1 - THREE.MathUtils.smoothstep(Math.abs(q.x), 0.014, 0.034)) * THREE.MathUtils.smoothstep(q.z, 0.06, 0.08)];
function rigJaw() {
  const mand = byName.get("Mandible"); if (!mand) return;
  const pts = [], v = new THREE.Vector3();
  for (const m of mand) { const p = m.geometry.attributes.position; for (let i = 0; i < p.count; i++) pts.push(v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld).clone()); }
  pts.sort((a, b) => b.y - a.y);
  const top = pts.slice(0, Math.max(10, Math.floor(pts.length * 0.01)));
  pivot.copy(top.reduce((a, b) => a.add(b), new THREE.Vector3()).divideScalar(top.length)); pivot.x = 0;
  for (const m of meshes) {
    const n = m.userData.name; let weight = null;
    if (RIGID.test(n)) weight = () => 1;
    else if (n === "Tongue") weight = (q) => 0.12 + 0.45 * THREE.MathUtils.smoothstep(q.z, 0.03, 0.075);   // stays up, so its top shows
    else if (/^Buccal mucosa/.test(n)) weight = (q) => THREE.MathUtils.smoothstep(-q.y, -1.542, -1.515);
    if (/^(Epidermis|Dermis|Hypodermis \(subcutaneous fat\))$/.test(n)) weight = skinJaw;
    const lift = LIFT[n] || (/^(Epidermis|Dermis|Hypodermis \(subcutaneous fat\))$/.test(n) ? SKIN_LIFT : null);
    // "say ahh": the back of the tongue presses down and forward, opening the view to the uvula and tonsils
    const ahh = n === "Tongue" ? (q) => THREE.MathUtils.smoothstep(q.y, 1.512, 1.537) * THREE.MathUtils.smoothstep(-q.z, -0.075, -0.035) : null;
    if (!weight && !lift) continue;
    if (!weight) weight = () => 0;
    // The compressed file stores each mesh as 16-bit numbers inside its own
    // bounding box, so a vertex swung outside that box would be clamped flat.
    // Moving parts get full-precision world-space copies instead.
    const g = m.geometry, p = g.attributes.position, nrm = g.attributes.normal, mw = m.matrixWorld.clone(), nm = new THREE.Matrix3().getNormalMatrix(mw);
    const rest = [], w = [], restN = [], lw = [], dw = [];
    for (let i = 0; i < p.count; i++) { const q = v.fromBufferAttribute(p, i).applyMatrix4(mw).clone(); rest.push(q); w.push(weight(q)); lw.push(lift ? lift[1](q) : 0); dw.push(ahh ? ahh(q) : 0); }
    if (nrm) for (let i = 0; i < nrm.count; i++) restN.push(new THREE.Vector3(nrm.getX(i), nrm.getY(i), nrm.getZ(i)).applyMatrix3(nm).normalize());
    g.setAttribute("position", new THREE.Float32BufferAttribute(rest.flatMap((q) => [q.x, q.y, q.z]), 3));
    g.setAttribute("ocRest", new THREE.Float32BufferAttribute(rest.flatMap((q) => [q.x, q.y, q.z]), 3));
    m.material.userData.u.uRig.value = 1;
    if (nrm) g.setAttribute("normal", new THREE.Float32BufferAttribute(restN.flatMap((q) => [q.x, q.y, q.z]), 3));
    scene.add(m); m.position.set(0, 0, 0); m.quaternion.identity(); m.scale.set(1, 1, 1); m.updateMatrixWorld(true);
    // only the vertices that ever move are updated (the skin is large and mostly still)
    const idx = []; for (let i = 0; i < rest.length; i++) if (w[i] > 0 || lw[i] > 0 || dw[i] > 0) idx.push(i);
    rigged.push({ m, name: n, rest, idx, w, lw, dw: ahh ? dw : null, lift: lift ? lift[0] : null, inv: new THREE.Matrix4(), restN: nrm ? restN : null });
  }
}
let jawNow = "";
function openJaw(k, ahh = 0, face = false) {
  if (jawNow === k + "/" + ahh + "/" + face) return; jawNow = k + "/" + ahh + "/" + face;
  const q = new THREE.Vector3(), axis = new THREE.Vector3(1, 0, 0), rot = new THREE.Quaternion();
  for (const r of rigged) {
    const p = r.m.geometry.attributes.position, nrm = r.m.geometry.attributes.normal;
    for (const i of r.idx) {
      rot.setFromAxisAngle(axis, k * JAW_MAX * r.w[i]);
      q.copy(r.rest[i]).sub(pivot).applyQuaternion(rot).add(pivot);
      if (r.lift) q.addScaledVector(r.lift, k * r.lw[i] * (face && /^Lower (lip|labial)/.test(r.name) ? 0 : 1));
      if (r.dw) { q.y -= 0.011 * ahh * r.dw[i]; q.z += 0.003 * ahh * r.dw[i]; }
      q.applyMatrix4(r.inv);
      p.setXYZ(i, q.x, q.y, q.z);
      if (r.restN && nrm) { q.copy(r.restN[i]).applyQuaternion(rot); nrm.setXYZ(i, q.x, q.y, q.z); }
    }
    p.needsUpdate = true; if (nrm) nrm.needsUpdate = true; r.m.geometry.computeBoundingSphere(); r.m.geometry.computeBoundingBox();
  }
}

// ---- state -------------------------------------------------------------------
// Peeled to bone, only the skeleton and teeth stay (Ian, 22 Oct: no eyeballs, cartilage or gums there).
function visibleByDepth(cls) { return state.depth === 3 ? cls === "bone" || cls === "tooth" : (DEPTH_OF[cls] ?? 5) >= state.depth; }
function apply() {
  const planes = [];
  state.planes.forEach((pl, i) => {
    SHARED.planeOn.value[i] = pl ? 1 : 0;
    if (!pl) return;
    const n = [new THREE.Vector3(-1, 0, 0), new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, -1, 0)][i].clone().multiplyScalar(pl.flip ? -1 : 1);
    const at = center.clone().add(new THREE.Vector3(...[[1, 0, 0], [0, 0, 1], [0, 1, 0]][i]).multiplyScalar(pl.offset || 0));
    CLIP[i].setFromNormalAndCoplanarPoint(n, at);
    SHARED.planes.value[i].set(CLIP[i].normal.x, CLIP[i].normal.y, CLIP[i].normal.z, CLIP[i].constant);
    planes.push(CLIP[i]);
  });
  const xray = state.mode === "xray", mouth = state.mode === "mouth";
  openJaw(mouth ? state.open : 0, mouth ? state.ahh || 0 : 0, mouth && !!state.face);
  if (block) block.visible = !!state.block;
  for (const m of meshes) {
    const cls = m.userData.cls, hl = state.hl.has(m);
    if (m.userData.block) { m.visible = !!state.block; continue; }
    if (state.block) { m.visible = false; continue; }
    // see-through: only skin, bone, teeth and cartilage stay, as glass; a
    // thousand overlapping glass layers would fog everything else out
    // Lips are shown where they belong, in the face: painted on the skin in the Skin view. Without the
    // face around them, the swept lips read as loose bands across an open mouth, so the Mouth view is
    // a cutaway of the inside, linings seen from within.
    // With the face on, the open mouth is seen as in life, inside the face (a mouth on a bare skull
    // looked uncanny, Ian, 22 Oct); with it off, the mouth is a cutaway seen from any side.
    // Only the outer skin: the inner layers crumple where the skin is thinnest, under the nose.
    const face = mouth && state.face && (cls === "epidermis" || cls === "eye" || cls === "hair");
    // The skin view, uncut, draws only what can be seen: the atlas puts some muscle and vessels just
    // outside the skin (round the ear, beside the nose), and they showed through it as holes.
    const skinOnly = !mouth && !xray && state.depth === 0 && !state.planes.some(Boolean) && !state.block
      && !["epidermis", "hair", "eye"].includes(cls);
    // the linings of the closed mouth stay out of the whole-head views; with no skin on the head (23 Oct) the
    // inner lips would float as strips in front of the teeth, so those stay out unless the head is cut
    const closedFace = !mouth && !xray && (state.depth === 0 && /^(Upper labial mucosa|Lower labial mucosa|Floor of mouth mucosa|Buccal mucosa)/.test(m.userData.name)
      || !state.planes.some(Boolean) && /^(Upper labial mucosa|Lower labial mucosa)/.test(m.userData.name));
    m.visible = (CRUDE.test(m.userData.name) || cls === "lip" || closedFace || skinOnly || mouth && /^Soft palate$/.test(m.userData.name)) && !hl ? false : xray ? hl || GHOSTED.has(cls) : mouth ? hl || face || MOUTH.has(cls) || cls === "bone" : visibleByDepth(cls) || hl;
    m.material.clippingPlanes = hl && xray ? [] : planes;
    m.material.clipIntersection = !!state.cutaway;
    const ghost = (xray && !hl) || (mouth && cls === "bone" && !hl && !JAWBONE.test(m.userData.name)) ? 1 : 0;
    m.material.userData.u.uGhost.value = ghost;
    m.material.userData.u.uHL.value = hl ? 1 : 0;
    m.material.userData.u.uNoFront.value = !xray && (cls === "dermis" || cls === "hypodermis") && (mouth || visibleByDepth("epidermis")) ? 1 : 0;
    // highlights are drawn after the glass (transparent queue, later order) so the glass never veils them
    m.material.transparent = !!ghost || (xray && hl) || !!m.userData.glass; m.material.depthWrite = !ghost && !m.userData.glass;
    m.renderOrder = ghost ? 10 : hl && xray ? 20 : 0;
  }
}

function view(az, el, dist, target) {
  const t = target ? new THREE.Vector3(...target) : center;
  const a = az * Math.PI / 180, e = el * Math.PI / 180, r = dist * size * 0.5;
  camera.position.set(t.x + Math.sin(a) * Math.cos(e) * r, t.y + Math.sin(e) * r, t.z + Math.cos(a) * Math.cos(e) * r);
  controls.target.copy(t); camera.lookAt(t); controls.update();
}

function find(pattern) {
  const re = pattern instanceof RegExp ? pattern : new RegExp(pattern, "i");
  return meshes.filter((m) => re.test(m.userData.name));
}

// ---- pointing at what is named --------------------------------------------------
// A label's leader ends on a point of the named structure that the camera can
// actually see: sample its vertices, keep those whose ray from the camera hits
// that structure first (cut-away and see-through parts do not block), and take
// the one nearest the middle of the visible ones.
const ray = new THREE.Raycaster();
function clippedAway(p) { return state.planes.some((pl, i) => pl && CLIP[i].distanceToPoint(p) < 0); }
function blocks(m) {
  if (!m.visible) return false;
  if (state.mode === "xray" && !state.hl.has(m)) return false;
  if (m.material.userData && m.material.userData.u && m.material.userData.u.uGhost.value > 0) return false;   // glass never hides anything
  if (m.userData.glass) return false;          // nor do the cornea and lens
  return true;
}
// What is on screen, exactly: every drawn structure rendered once in its own
// flat colour (with the same cuts), read back as a buffer of structure ids.
// Labels and taps look things up here instead of raycasting a thousand meshes.
const idTarget = new THREE.WebGLRenderTarget(1, 1, { depthBuffer: true });
const idMats = new Map();
function idMaterial(i) {
  let m = idMats.get(i);
  if (!m) {
    m = new THREE.ShaderMaterial({
      uniforms: { uId: { value: new THREE.Vector3((i & 255) / 255, ((i >> 8) & 255) / 255, ((i >> 16) & 255) / 255) } },
      vertexShader: "#include <common>\n#include <clipping_planes_pars_vertex>\nvoid main(){\n#include <begin_vertex>\n#include <project_vertex>\n#include <clipping_planes_vertex>\n}",
      fragmentShader: "uniform vec3 uId;\n#include <clipping_planes_pars_fragment>\nvoid main(){\n#include <clipping_planes_fragment>\ngl_FragColor = vec4(uId, 1.0);\n}",
      side: THREE.DoubleSide, clipping: true,
    });
    idMats.set(i, m);
  }
  return m;
}
let idBuf = null, idW = 0, idH = 0;
function idPass() {
  idW = Math.max(1, Math.round(W)); idH = Math.max(1, Math.round(H));
  idTarget.setSize(idW, idH);
  const saved = [], tm = renderer.toneMapping, bg = scene.background;
  meshes.forEach((m, i) => {
    saved.push([m, m.material, m.visible]);
    if (!blocks(m)) { m.visible = false; return; }
    const mat = idMaterial(i + 1), src = Array.isArray(m.material) ? m.material[0] : m.material;
    mat.clippingPlanes = src.clippingPlanes; mat.clipIntersection = src.clipIntersection; mat.side = src.side; m.material = mat;
  });
  renderer.toneMapping = THREE.NoToneMapping; scene.background = null;
  renderer.setRenderTarget(idTarget); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera); renderer.setRenderTarget(null);
  renderer.toneMapping = tm; scene.background = bg;
  saved.forEach(([m, mat, vis]) => { m.material = mat; m.visible = vis; });
  idBuf = new Uint8Array(idW * idH * 4); renderer.readRenderTargetPixels(idTarget, 0, 0, idW, idH, idBuf);
}
function idAt(x, y) {                        // screen pixel (top-left origin) -> mesh or null
  const px = Math.round(x), py = Math.round(idH - 1 - y);
  if (px < 0 || py < 0 || px >= idW || py >= idH) return null;
  const o = (py * idW + px) * 4, i = idBuf[o] | (idBuf[o + 1] << 8) | (idBuf[o + 2] << 16);
  return i ? meshes[i - 1] : null;
}
// `within` limits a label to part of a mesh ([[x0,y0,z0],[x1,y1,z1]]): the lips are painted on the skin, so
// "Lips" must land inside the lip area, not anywhere on the skin.
function insideBox(p, b) { return !b || (p.x >= b[0][0] && p.y >= b[0][1] && p.z >= b[0][2] && p.x <= b[1][0] && p.y <= b[1][1] && p.z <= b[1][2]); }
function visiblePoint(targets, near, within) {
  camera.updateMatrixWorld(); idPass();
  const set = new Set(targets), cands = [], v = new THREE.Vector3();
  for (const m of targets) {
    if (!m.visible) continue;
    const p = m.geometry.attributes.position, step = Math.max(1, Math.floor(p.count / 600));
    for (let i = 0; i < p.count; i += step) {
      v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld);
      if (clippedAway(v) || !insideBox(v, within)) continue;
      const q = v.clone().project(camera); if (q.z > 1) continue;
      const x = (q.x * 0.5 + 0.5) * W, y = (-q.y * 0.5 + 0.5) * H;
      if (set.has(idAt(x, y))) cands.push({ p: v.clone(), x, y });
    }
  }
  if (!cands.length) return null;
  // Rank: toward `near` for a named part ("sides of the tongue"), otherwise
  // nearest the middle of what is visible. Then take the first whose dot sits
  // inside a patch of the target, so it never lands on an edge or a thread.
  let order;
  if (near) {
    const c = cands.reduce((a, b) => a.add(b.p), new THREE.Vector3()).divideScalar(cands.length), d = new THREE.Vector3(...near).normalize();
    order = cands.map((k) => [k, -k.p.clone().sub(c).dot(d)]);
  } else {
    const mx = cands.reduce((a, k) => a + k.x, 0) / cands.length, my = cands.reduce((a, k) => a + k.y, 0) / cands.length;
    order = cands.map((k) => [k, Math.hypot(k.x - mx, k.y - my)]);
  }
  order.sort((a, b) => a[1] - b[1]);
  // a 9 px patch where the structure allows it, then 3 px, then the exact pixel for hair-thin nerves
  for (const R of [4.5, 1.5, 0]) for (const [k] of order.slice(0, 300)) {
    if ([[0, 0], [R, 0], [-R, 0], [0, R], [0, -R]].every(([dx, dy]) => set.has(idAt(k.x + dx, k.y + dy)))) return k.p;
  }
  return null;
}

// Labels stack down one side of the frame each, in the order of their dots
// from top to bottom, so leader lines do not cross.
function drawLabel() {
  const svg = document.getElementById("lead"), tags = document.getElementById("tags");
  const live = state.labels.filter((l) => l.point);
  while (tags.children.length < live.length) {
    const d = document.createElement("div"); d.className = "tag"; d.innerHTML = "<b></b><span></span>"; tags.appendChild(d);
    svg.insertAdjacentHTML("beforeend", "<g><line/><circle r='5'/></g>");
  }
  [...tags.children].forEach((d, i) => { d.style.display = i < live.length ? "" : "none"; });
  [...svg.children].forEach((g, i) => { g.style.display = i < live.length ? "" : "none"; });
  const pts = live.map((l) => { const p = l.point.clone().project(camera); return { l, x: (p.x * 0.5 + 0.5) * W, y: (-p.y * 0.5 + 0.5) * H }; });
  pts.forEach((q) => { q.left = q.l.side ? q.l.side === "left" : q.x > W / 2; });
  const slot = { true: H * 0.1, false: H * 0.1 };
  pts.sort((a, b) => a.y - b.y).forEach((q, i) => {
    const d = tags.children[i], g = svg.children[i];
    d.querySelector("b").textContent = q.l.title; d.querySelector("span").textContent = q.l.sub || "";
    const by = Math.max(slot[q.left], Math.min(q.y - 30, H * 0.82));
    d.style.maxWidth = W * 0.34 + "px"; d.style.top = by + "px"; d.style.textAlign = q.left ? "left" : "right";
    if (q.left) { d.style.left = W * 0.04 + "px"; d.style.right = "auto"; } else { d.style.right = W * 0.04 + "px"; d.style.left = "auto"; }
    slot[q.left] = by + d.offsetHeight + 12;
    const bw = d.offsetWidth, ax = q.left ? W * 0.04 + bw + 6 : W - W * 0.04 - bw - 6, ay = by + d.offsetHeight / 2;
    const ln = g.querySelector("line"), c = g.querySelector("circle");
    ln.setAttribute("x1", q.x); ln.setAttribute("y1", q.y); ln.setAttribute("x2", ax); ln.setAttribute("y2", ay);
    c.setAttribute("cx", q.x); c.setAttribute("cy", q.y);
  });
}

function loop() {
  requestAnimationFrame(loop);
  if (!ready) return;
  if (!window.OC_SCRIPTED) controls.update();
  aimExam(); renderer.render(scene, camera); drawLabel();
}
loop();

// ---- scripting surface -------------------------------------------------------------
window.oc = {
  view,
  mode(m) { state.mode = m; apply(); },
  // open 0..1 (up to 1.3 for "ahh"); ahh 0..1 lowers the back of the tongue; face shows the skin around the mouth
  mouth(open = 1, ahh = 0, face = false) { state.mode = "mouth"; state.open = open; state.ahh = ahh; state.face = face; apply(); },
  depth(d) { state.depth = d; apply(); },
  planes(spec) {                              // {sagittal: {offset, flip}, coronal: ..., axial: ...}
    state.planes = ["sagittal", "coronal", "axial"].map((k) => (spec && spec[k]) || null);
    state.cutaway = spec && spec.cutaway; apply();
  },
  block(on) {                                 // the stepped tissue block in place of the head
    state.block = on; apply();
    if (on) { const t = new THREE.Vector3(0.002, 0.008, 0); camera.position.set(0.05, 0.05, 0.07); controls.target.copy(t); camera.lookAt(t); controls.update(); }
  },
  highlight(pattern) { state.hl = new Set(pattern ? find(pattern) : []); apply(); },
  label(pattern, title, sub, side, near, within) { state.labels = []; return pattern ? this.addLabel(pattern, title, sub, side, near, within) : null; },
  addLabel(pattern, title, sub, side, near, within) {
    const t = find(pattern); scene.updateMatrixWorld(true); camera.updateMatrixWorld();
    const l = { title, sub, side, point: t.length ? visiblePoint(t, near, within) : null, pattern, within }; state.labels.push(l);
    return l.point ? l.point.toArray() : null;
  },
  names: () => [...byName.keys()].sort(),
  dump(name, x0, x1, y0, y1, zmin) {         // world vertices of a mesh inside a box (for fitting generated parts)
    const out = [], v = new THREE.Vector3();
    for (const m of byName.get(name) || []) { const p = m.geometry.attributes.position;
      for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld);
        if (v.x >= x0 && v.x <= x1 && v.y >= y0 && v.y <= y1 && v.z >= zmin) out.push([+v.x.toFixed(4), +v.y.toFixed(4), +v.z.toFixed(4)]); } }
    return out;
  },
  lips(o) {                                   // tune the lips' colour and show where the mouth would open
    const a = SHARED.lipA.value, b = SHARED.lipB.value;
    if (o) {
      if (o.line != null) a.x = o.line; if (o.upper != null) a.y = o.upper; if (o.lower != null) a.z = o.lower; if (o.width != null) a.w = o.width;
      if (o.bow != null) b.x = o.bow; if (o.opening != null) b.y = o.opening; if (o.guide != null) b.z = o.guide ? 1 : 0;
    }
    return { line: a.x, upper: a.y, lower: a.z, width: a.w, bow: b.x, opening: b.y, guide: b.z > 0.5 };
  },
  project(x, y, z) { camera.updateMatrixWorld(); const p = new THREE.Vector3(x, y, z).project(camera); return [(p.x * 0.5 + 0.5) * W, (-p.y * 0.5 + 0.5) * H]; },
  check() {                                   // what is actually under each label's dot
    camera.updateMatrixWorld(); idPass();
    return state.labels.map((l) => {
      if (!l.point) return { title: l.title, ok: false, hit: null };
      const p = l.point.clone().project(camera), hit = this.pick((p.x * 0.5 + 0.5) * W, (-p.y * 0.5 + 0.5) * H, false);
      const re = new RegExp(l.pattern, "i");
      return { title: l.title, ok: !!hit && re.test(hit.name) && insideBox(new THREE.Vector3(...hit.point), l.within), hit: hit && hit.name };
    });
  },
  probe(name, x, y, z) {                     // nearest vertex of a mesh to a point, with its normal
    const m = (byName.get(name) || [])[0]; if (!m) return null;
    const p = m.geometry.attributes.position, n = m.geometry.attributes.normal, t = new THREE.Vector3(x, y, z), v = new THREE.Vector3();
    let best = 0, bd = 1e9; for (let i = 0; i < p.count; i++) { const d = v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld).distanceTo(t); if (d < bd) { bd = d; best = i; } }
    const nn = n ? new THREE.Vector3(n.getX(best), n.getY(best), n.getZ(best)).transformDirection(m.matrixWorld).toArray() : null;
    return { p: v.fromBufferAttribute(p, best).applyMatrix4(m.matrixWorld).toArray(), n: nn, d: bd };
  },
  _meshes: (name) => byName.get(name) || [],          // for debugging scripts
  boxes: () => meshes.map((m) => { const b = new THREE.Box3().setFromObject(m); return [m.userData.name, m.userData.cls, b.min.toArray().map((x) => +x.toFixed(3)), b.max.toArray().map((x) => +x.toFixed(3))]; }),
  classes: () => meshes.reduce((a, m) => (a[m.userData.cls] = (a[m.userData.cls] || 0) + 1, a), {}),
  center: () => center.toArray(), size: () => size,
  render() { controls.update(); aimExam(); renderer.render(scene, camera); drawLabel(); return true; },
  pick(x, y, fresh = true) {                  // what is under a screen point
    camera.updateMatrixWorld(); if (fresh || !idBuf) idPass();
    const m = idAt(x, y); if (!m) return null;
    ray.setFromCamera(new THREE.Vector2(x / W * 2 - 1, -(y / H) * 2 + 1), camera); ray.far = 100;
    const hit = ray.intersectObject(m, false).find((h) => !clippedAway(h.point));
    const point = hit ? hit.point : ray.ray.at(camera.position.distanceTo(controls.target), new THREE.Vector3());
    return { name: m.userData.name, cls: m.userData.cls, point: point.toArray() };
  },
  labelAt(x, y) {                             // label whatever is under a screen point
    const hit = this.pick(x, y); if (!hit) { state.labels = []; return null; }
    const t = (byName.get(hit.name) || []); state.hl = new Set(state.mode === "xray" ? state.hl : []);
    state.labels = [{ title: hit.name.replace(/\.(l|r)$/, (m) => (m === ".l" ? " (left)" : " (right)")).replace(/ \(block\)$/, ""), sub: hit.cls, point: new THREE.Vector3(...hit.point), pattern: "." }];
    return hit;
  },
  clearLabels() { state.labels = []; },
  tune(cls, uniform, value) {                 // set a shader uniform on every material of a tissue class (for tuning)
    for (const m of meshes) if (m.userData.cls === cls) (Array.isArray(m.material) ? m.material : [m.material]).forEach((mm) => { if (mm.userData.u && mm.userData.u[uniform]) mm.userData.u[uniform].value = value; });
  },
  pointAt(name, title) {                      // label one exact mesh name
    const t = byName.get(name) || []; scene.updateMatrixWorld(true);
    state.labels = [{ title: title || name, sub: "", point: t.length ? visiblePoint(t) : null, pattern: "^" + name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "$" }];
  },
};
