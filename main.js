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

function constructGeometry(model) {
    // Convert vertices to Float32Array for BufferGeometry. PolyhedronGeometry on the other hand doesn't need this conversion
    const vertices = new Float32Array(model.vertices);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    geometry.setIndex(model.faces);
    geometry.computeVertexNormals();
    return geometry;
}

function setPolyhedronModel(model) {
    const geometry = constructGeometry(model);
    polyhedron.geometry.dispose();
    polyhedron.geometry = geometry;
}

function updateCurrentModel(operation) {
    if (operation === 'rectify') {
        rectifyPolytope();
    } else if (operation === 'stellate') {
        stellatePolytope();
    } else if (operation === 'separate') {
        separatePolytope();
    }
    setPolyhedronModel(current_model);
}

// Construct geometry
const geometry = constructGeometry(current_model);

// Create mesh
const material = new THREE.MeshLambertMaterial({
    color: 0x9a9aae,
    side: THREE.DoubleSide,
    flatShading: true
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

const btnRectify = document.getElementById('btn-rectify');
const btnStellate = document.getElementById('btn-stellate');
const btnSeparate = document.getElementById('btn-separate');

btnRectify?.addEventListener('click', () => updateCurrentModel('rectify'));
btnStellate?.addEventListener('click', () => updateCurrentModel('stellate'));
btnSeparate?.addEventListener('click', () => updateCurrentModel('separate'));

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