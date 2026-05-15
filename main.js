import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

//Default mode
var mode = "faces"

// Renderer
const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

// Scene
const scene = new THREE.Scene();

// Camera
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 3;

const geometry = new THREE.PolyhedronGeometry(current_model.vertices, current_model.faces, 1, 0);

// Create mesh
const material = new THREE.MeshLambertMaterial({
    color: 0x9a9aae,
    side: THREE.DoubleSide
});
const polyhedron = new THREE.Mesh( geometry, material );
scene.add(polyhedron);

// Ambient light
const ambientLight = new THREE.AmbientLight(0xffffff, 0.2)
scene.add(ambientLight)

// Directional light
const directionalLight = new THREE.DirectionalLight(0x00fffc, 0.9)
directionalLight.position.set(0.1, 0.2, 1)
camera.add(directionalLight)
scene.add(camera)

// // const points = [];
// // points.push( new THREE.Vector3( - 10, 0, 0 ) );
// // points.push( new THREE.Vector3( 0, 10, 0 ) );
// // points.push( new THREE.Vector3( 10, 0, 0 ) );
// // const geometry = new THREE.BufferGeometry().setFromPoints( points );
// // const material = new THREE.LineBasicMaterial( { color: 0x0000ff } );
// // const line = new THREE.Line( geometry, material );
// const line = new THREE.Line( geometry, material );
// // scene.add( line );

// Rotation controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; // Optional: for smoother rotation
controls.dampingFactor = 0.05; // Optional: for smoother rotation

function animate() {
    // polyhedron.rotation.x += 0.00005;
    // polyhedron.rotation.y += 0.00005;
    requestAnimationFrame(animate);
    controls.update(); // Required if enableDamping is true
    if (mode == "faces") {
	    renderer.render( scene, camera );
    }
}
renderer.setAnimationLoop( animate );