
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Interactive Digital Sphere",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
.block-container {padding:0 !important; max-width:100% !important;}
[data-testid="stAppViewContainer"] {background:#01060b;}
[data-testid="stHeader"] {background:transparent;}
iframe {border:0 !important;}
</style>
""", unsafe_allow_html=True)

html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
html,body,#sphere{margin:0;width:100%;height:100%;overflow:hidden;background:transparent}
#sphere{position:absolute;inset:0;cursor:grab}
#sphere:active{cursor:grabbing}
canvas{display:block;width:100%;height:100%}
</style>
</head>
<body>
<div id="sphere" aria-label="Interactive transparent digital sphere"></div>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";

const el=document.getElementById("sphere");
const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;

const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(42,1,.1,100);
camera.position.set(0,0,7.2);

const renderer=new THREE.WebGLRenderer({
  antialias:true,
  alpha:true,
  powerPreference:"high-performance"
});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(1,1);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.1;
el.appendChild(renderer.domElement);

const root=new THREE.Group();
scene.add(root);

// --- Transparent particle sphere: no filled globe and no blue outer circle ---
const count=6200;
const pos=new Float32Array(count*3);

for(let i=0;i<count;i++){
  const z=Math.random()*2-1;
  const a=Math.random()*Math.PI*2;
  const r=Math.sqrt(1-z*z);
  const radius=1.72+Math.random()*.045;

  pos[i*3]=radius*r*Math.cos(a);
  pos[i*3+1]=radius*z;
  pos[i*3+2]=radius*r*Math.sin(a);
}

const particleGeo=new THREE.BufferGeometry();
particleGeo.setAttribute("position",new THREE.BufferAttribute(pos,3));

const particleMat=new THREE.PointsMaterial({
  color:0x9ddfff,
  size:.0125,
  transparent:true,
  opacity:.78,
  depthWrite:false,
  blending:THREE.AdditiveBlending
});

const particleGlobe=new THREE.Points(particleGeo,particleMat);
root.add(particleGlobe);

// Brighter data nodes
const nodeCount=95;
const nodePos=new Float32Array(nodeCount*3);

for(let i=0;i<nodeCount;i++){
  const z=Math.random()*2-1;
  const a=Math.random()*Math.PI*2;
  const r=Math.sqrt(1-z*z);
  const radius=1.735;

  nodePos[i*3]=radius*r*Math.cos(a);
  nodePos[i*3+1]=radius*z;
  nodePos[i*3+2]=radius*r*Math.sin(a);
}

const nodeGeo=new THREE.BufferGeometry();
nodeGeo.setAttribute("position",new THREE.BufferAttribute(nodePos,3));

root.add(new THREE.Points(
  nodeGeo,
  new THREE.PointsMaterial({
    color:0xe2f8ff,
    size:.026,
    transparent:true,
    opacity:.92,
    depthWrite:false,
    blending:THREE.AdditiveBlending
  })
));

// Very subtle orbital lines — no enclosing shell
function orbit(rx,ry,rz,sx,sy,opacity,speed){
  const curve=new THREE.EllipseCurve(
    0,0,2.15*sx,.72*sy,0,Math.PI*2,false,0
  );

  const pts=curve.getPoints(260).map(
    p=>new THREE.Vector3(p.x,p.y,0)
  );

  const line=new THREE.LineLoop(
    new THREE.BufferGeometry().setFromPoints(pts),
    new THREE.LineBasicMaterial({
      color:0x7ddcff,
      transparent:true,
      opacity,
      depthWrite:false,
      blending:THREE.AdditiveBlending
    })
  );

  line.rotation.set(rx,ry,rz);
  line.userData.speed=speed;
  root.add(line);
  return line;
}

const orbits=[
  orbit(1.02,.18,.2,1,.98,.26,.018),
  orbit(1.68,-.52,-.34,1.03,.88,.16,-.012),
  orbit(.48,1.15,.8,.92,1.1,.13,.014)
];

// Sparse particles outside the sphere
const floatCount=180;
const floatPos=new Float32Array(floatCount*3);

for(let i=0;i<floatCount;i++){
  const a=Math.random()*Math.PI*2;
  const b=Math.acos(2*Math.random()-1);
  const r=2.15+Math.random()*1.25;

  floatPos[i*3]=r*Math.sin(b)*Math.cos(a);
  floatPos[i*3+1]=r*Math.cos(b);
  floatPos[i*3+2]=r*Math.sin(b)*Math.sin(a);
}

const floatGeo=new THREE.BufferGeometry();
floatGeo.setAttribute("position",new THREE.BufferAttribute(floatPos,3));

const floating=new THREE.Points(
  floatGeo,
  new THREE.PointsMaterial({
    color:0x55b9ed,
    size:.010,
    transparent:true,
    opacity:.28,
    depthWrite:false,
    blending:THREE.AdditiveBlending
  })
);
scene.add(floating);

// Lighting is intentionally subtle because there is no solid globe.
scene.add(new THREE.AmbientLight(0x0a2030,.5));

let mouseX=0,mouseY=0,targetX=0,targetY=0;
let dragging=false,sx=0,sy=0,rx=0,ry=0;

el.addEventListener("pointermove",e=>{
  const r=el.getBoundingClientRect();
  const px=(e.clientX-r.left)/r.width-.5;
  const py=(e.clientY-r.top)/r.height-.5;

  targetY=px*.30;
  targetX=-py*.18;

  if(dragging){
    root.rotation.y=ry+(e.clientX-sx)*.0032;
    root.rotation.x=rx+(e.clientY-sy)*.0032;
  }
});

el.addEventListener("pointerleave",()=>{
  targetX=0;
  targetY=0;
});

el.addEventListener("pointerdown",e=>{
  dragging=true;
  sx=e.clientX;
  sy=e.clientY;
  rx=root.rotation.x;
  ry=root.rotation.y;
  el.setPointerCapture(e.pointerId);
});

el.addEventListener("pointerup",e=>{
  dragging=false;
  el.releasePointerCapture(e.pointerId);
});

const clock=new THREE.Clock();

function animate(){
  requestAnimationFrame(animate);
  const t=clock.getElapsedTime();

  mouseX+=(targetX-mouseX)*.045;
  mouseY+=(targetY-mouseY)*.045;

  if(!dragging){
    root.rotation.x+=(mouseX-root.rotation.x)*.018;
    root.rotation.y+=mouseY*.005;

    if(!reduced){
      root.rotation.y+=.00055;
    }
  }

  particleGlobe.rotation.y=t*.0045;
  floating.rotation.y=-t*.0015;

  orbits.forEach(o=>{
    o.rotation.z+=o.userData.speed;
  });

  renderer.render(scene,camera);
}

function resize(){
  const w=Math.max(1,el.clientWidth);
  const h=Math.max(1,el.clientHeight);

  camera.aspect=w/h;
  camera.updateProjectionMatrix();

  renderer.setSize(w,h,false);
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
}

addEventListener("resize",resize);
resize();
animate();
</script>
</body>
</html>
"""

components.html(html, height=780, scrolling=False)
