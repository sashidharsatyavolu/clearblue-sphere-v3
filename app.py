
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
html, body, [data-testid="stAppViewContainer"], .stApp {
    background:#01060b !important;
}
#MainMenu, footer, header {visibility:hidden;}
.block-container {padding:0 !important; max-width:100% !important;}
iframe {border:0 !important; display:block !important;}
</style>
""", unsafe_allow_html=True)

html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
html,body,#stage{margin:0;width:100%;height:100%;overflow:hidden;background:#01060b}
#stage{position:absolute;inset:0}
canvas{display:block;width:100%;height:100%}
#error{
 position:absolute;left:20px;top:20px;color:#8edcff;
 font:12px/1.5 system-ui,sans-serif;display:none
}
</style>
</head>
<body>
<div id="stage"></div>
<div id="error"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const stage=document.getElementById("stage");
  const error=document.getElementById("error");

  if(!window.THREE){
    error.style.display="block";
    error.textContent="Three.js could not be loaded.";
    return;
  }

  try {
    const scene=new THREE.Scene();
    const camera=new THREE.PerspectiveCamera(40,1,0.1,100);
    camera.position.z=6.4;

    const renderer=new THREE.WebGLRenderer({
      antialias:true,
      alpha:true,
      powerPreference:"high-performance"
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
    renderer.setClearColor(0x000000,0);
    stage.appendChild(renderer.domElement);

    const root=new THREE.Group();
    scene.add(root);

    // Transparent particle sphere — deliberately no solid globe and no outer blue shell.
    const count=6000;
    const positions=new Float32Array(count*3);

    for(let i=0;i<count;i++){
      const z=Math.random()*2-1;
      const a=Math.random()*Math.PI*2;
      const r=Math.sqrt(1-z*z);
      const radius=1.58+Math.random()*0.045;
      positions[i*3]=radius*r*Math.cos(a);
      positions[i*3+1]=radius*z;
      positions[i*3+2]=radius*r*Math.sin(a);
    }

    const geo=new THREE.BufferGeometry();
    geo.setAttribute("position",new THREE.BufferAttribute(positions,3));

    const points=new THREE.Points(
      geo,
      new THREE.PointsMaterial({
        color:0x9edfff,
        size:0.014,
        transparent:true,
        opacity:0.78,
        depthWrite:false,
        blending:THREE.AdditiveBlending
      })
    );
    root.add(points);

    // Bright nodes
    const nodes=90;
    const np=new Float32Array(nodes*3);
    for(let i=0;i<nodes;i++){
      const z=Math.random()*2-1;
      const a=Math.random()*Math.PI*2;
      const r=Math.sqrt(1-z*z);
      const radius=1.60;
      np[i*3]=radius*r*Math.cos(a);
      np[i*3+1]=radius*z;
      np[i*3+2]=radius*r*Math.sin(a);
    }

    const ng=new THREE.BufferGeometry();
    ng.setAttribute("position",new THREE.BufferAttribute(np,3));
    root.add(new THREE.Points(
      ng,
      new THREE.PointsMaterial({
        color:0xe7faff,
        size:0.028,
        transparent:true,
        opacity:0.95,
        depthWrite:false,
        blending:THREE.AdditiveBlending
      })
    ));

    // Very subtle orbital rings
    function makeOrbit(rx,ry,rz,sx,sy,opacity,speed){
      const curve=new THREE.EllipseCurve(
        0,0,2.0*sx,0.70*sy,0,Math.PI*2,false,0
      );
      const pts=curve.getPoints(220).map(
        p=>new THREE.Vector3(p.x,p.y,0)
      );
      const g=new THREE.BufferGeometry().setFromPoints(pts);
      const m=new THREE.LineBasicMaterial({
        color:0x7ddcff,
        transparent:true,
        opacity:opacity,
        depthWrite:false,
        blending:THREE.AdditiveBlending
      });
      const line=new THREE.LineLoop(g,m);
      line.rotation.set(rx,ry,rz);
      line.userData.speed=speed;
      root.add(line);
      return line;
    }

    const orbits=[
      makeOrbit(1.05,0.20,0.18,1.0,1.0,0.22,0.012),
      makeOrbit(1.70,-0.50,-0.30,1.02,0.86,0.13,-0.009),
      makeOrbit(0.45,1.10,0.78,0.92,1.05,0.10,0.010)
    ];

    // A few surrounding points
    const outside=150;
    const op=new Float32Array(outside*3);
    for(let i=0;i<outside;i++){
      const a=Math.random()*Math.PI*2;
      const b=Math.acos(2*Math.random()-1);
      const r=1.95+Math.random()*1.0;
      op[i*3]=r*Math.sin(b)*Math.cos(a);
      op[i*3+1]=r*Math.cos(b);
      op[i*3+2]=r*Math.sin(b)*Math.sin(a);
    }
    const og=new THREE.BufferGeometry();
    og.setAttribute("position",new THREE.BufferAttribute(op,3));
    const outsidePoints=new THREE.Points(
      og,
      new THREE.PointsMaterial({
        color:0x55b9ed,
        size:0.010,
        transparent:true,
        opacity:0.25,
        depthWrite:false,
        blending:THREE.AdditiveBlending
      })
    );
    scene.add(outsidePoints);

    let tx=0,ty=0,mx=0,my=0;
    let dragging=false,startX=0,startY=0,startRX=0,startRY=0;

    stage.addEventListener("pointermove",function(e){
      const r=stage.getBoundingClientRect();
      const x=(e.clientX-r.left)/r.width-0.5;
      const y=(e.clientY-r.top)/r.height-0.5;
      tx=x*0.34;
      ty=-y*0.22;

      if(dragging){
        root.rotation.y=startRY+(e.clientX-startX)*0.003;
        root.rotation.x=startRX+(e.clientY-startY)*0.003;
      }
    });

    stage.addEventListener("pointerleave",function(){
      tx=0;ty=0;
    });

    stage.addEventListener("pointerdown",function(e){
      dragging=true;
      startX=e.clientX;startY=e.clientY;
      startRX=root.rotation.x;startRY=root.rotation.y;
      stage.setPointerCapture(e.pointerId);
    });

    stage.addEventListener("pointerup",function(e){
      dragging=false;
      if(stage.hasPointerCapture(e.pointerId))
        stage.releasePointerCapture(e.pointerId);
    });

    function resize(){
      const w=Math.max(1,stage.clientWidth);
      const h=Math.max(1,stage.clientHeight);
      camera.aspect=w/h;
      camera.updateProjectionMatrix();
      renderer.setSize(w,h,false);
    }

    window.addEventListener("resize",resize);
    resize();

    const clock=new THREE.Clock();

    function animate(){
      requestAnimationFrame(animate);
      const t=clock.getElapsedTime();

      mx+=(tx-mx)*0.045;
      my+=(ty-my)*0.045;

      if(!dragging){
        root.rotation.x+=(my-root.rotation.x)*0.018;
        root.rotation.y+=mx*0.004;
        root.rotation.y+=0.00055;
      }

      points.rotation.y=t*0.004;
      outsidePoints.rotation.y=-t*0.0015;

      orbits.forEach(o=>o.rotation.z+=o.userData.speed);

      renderer.render(scene,camera);
    }

    animate();
  } catch(err) {
    error.style.display="block";
    error.textContent="Sphere error: "+err.message;
  }
})();
</script>
</body>
</html>
"""

components.html(html, height=780, scrolling=False)
