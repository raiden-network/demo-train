
var particles = [];
var nums;
var particleDensity = 800;
var noiseScale = 800;
var maxLife = 10;
var	simulationSpeed = 0.3;
var fadeFrame = 0;
var backgroundColor;
var invertColors = false;

var landscapeParams;




function setup(){

	default_receiver = new Receiver('0x001fb32f0488d4e4bd956ebcf3fdcce3fcc83150', 1337);
	landscapeParams = new LandscapeParameters(default_receiver)
	noiseSeed(landscapeParams.noiseSeed);
	randomSeed(landscapeParams.randomSeed);

	nums = windowWidth * windowHeight / particleDensity;
	backgroundColor = color(20, 20, 20);
	createCanvas(windowWidth, windowHeight);
	background(backgroundColor);
	for(var i = 0; i < nums; i++){
		particles[i] = new Particle();
	}

	setInterval(queryReceiver, 10000);
}

function draw(){
	noStroke();
	
	++fadeFrame;
	if(fadeFrame % 5 == 0){
		if(invertColors){
			blendMode(ADD);
		} else {
			blendMode(DIFFERENCE);
		}
		fill(1, 1, 1);
		rect(0,0,width,height);

		if(invertColors){
			blendMode(DARKEST);
		} else {
			blendMode(LIGHTEST);
		}
		fill(backgroundColor);
		rect(0,0,width,height);
	}
	
	blendMode(BLEND);
	smooth();
	for(var i = 0; i < nums; i++){
		var iterations = map(i,0,nums,5,1);
		var radius = map(i,0,nums,2,6);
		
		particles[i].move(iterations);
		particles[i].checkEdge();
		
		var alpha = 255;
		var particleColor;
		var fadeRatio;
		fadeRatio = min(particles[i].life * 5 / maxLife, 1);
		fadeRatio = min((maxLife - particles[i].life) * 5 / maxLife, fadeRatio);
		// fix to case 2 for now
		var colorCase = 2; 
		switch(colorCase)
		{
			case 1:
				var lifeRatioGrayscale = min(255, (255 * particles[i].life / maxLife) + red(backgroundColor));
				particleColor = color(lifeRatioGrayscale, alpha * fadeRatio);
				break;
			case 2:
				particleColor = particles[i].color;
				break;
			case 3:
				particleColor = color(blue(particles[i].color) + 70, green(particles[i].color) + 20, red(particles[i].color) - 50);
				break;
		}
		if(invertColors){
			particleColor = color(255 - red(particleColor), 255 - green(particleColor), 255 - blue(particleColor));
		}
		fill(red(particleColor), green(particleColor), blue(particleColor), alpha * fadeRatio);
		particles[i].display(radius);
	} 
}

var receiverEndpoint = "http://localhost:5000/api/v1/provider/current";
var currentReceiver;

function queryReceiver () {
	httpGet(receiverEndpoint, 'json', false, onReceiver)
}

function onReceiver(data) {
	console.log(data)
	newReceiver = new Receiver(data.address, data.identifier);
	if (newReceiver != currentReceiver){
		currentReceiver = newReceiver;
		onNewReceiver();
	}
}

function onNewReceiver(){
	landscapeParams = new LandscapeParameters(currentReceiver);
	noiseSeed(landscapeParams.perlinSeed);
	randomSeed(landscapeParams.randomSeed);
	advanceVisual();
}

class Receiver{
	constructor (address, identifier) {
		// 20 byte hex string - 20 x 8bit slices
		// TODO strip 0x before! check regex
		this.address = address.replace(/^0x/, '');
		this.identifier = identifier
	}
	get byteSlices(){
		return this.address.match(/.{1,2}/g).map(x => parseInt(x, 16))
	}
}

function recombineSlices (slice1) {
	// takes multiple 8bit ints, converts them back to the hexstring,
	// concatenates the strings and converts the string to an int
}

class LandscapeParameters {
	constructor (receiver) {
		var bytes = receiver.byteSlices;
		this.color1 = color(
			 bytes[2],
			 bytes[3],
			 bytes[4]
			)
		this.color2 = calculateFirstTriadColor(
			bytes[2],
			bytes[3],
			bytes[4]
			)
		this.color3 = color(
			 bytes[5],
			 bytes[6],
			 bytes[7]
			)
		this.color4 = calculateFirstTriadColor(
			bytes[5],
			bytes[6],
			bytes[7]
			)
		// FIXME derive from address bytes
		this.perlinSeed = 1337;
		this.randomSeed = 1337;
	}
}


function calculateFirstTriadColor(r, g, b){
	return tinycolorToColor(tinycolor(r, g, b).triad()[1]);
}

function tinycolorToColor(tinycolor) {
	var col = tinycolor.toRgb();
	var new_color =  color(col.r, col.g, col.b, col.a);
	return new_color;
}

class Particle{
// member properties and initialization
constructor (){
	this.vel = createVector(0, 0);
	this.pos = createVector(random(0, width), random(0, height));
	this.life = random(0, maxLife);
	this.flip = int(random(0,2)) * 2 - 1;
	this.setColor();
}
	setColor() {
	var randColor = int(random(0,5));
	console.log
	switch(randColor)
	// FIXME convert the tinycolor from the triad properly
	{
		case 0:
			this.color = landscapeParams.color1;
			break;
		case 1:
			this.color = landscapeParams.color2;
			break;
		case 2:
			this.color = landscapeParams.color3;
			break;
		case 3:
			this.color = landscapeParams.color4;
			break;
		case 4:
			this.color = color(255,255,255);
			break;
	}
	// console.log(this.color);
	}
	
// member functions
	move(iterations){
		if((this.life -= 0.01666) < 0)
			this.respawn();
		while(iterations > 0){
			var angle = noise(this.pos.x/noiseScale, this.pos.y/noiseScale)*TWO_PI*noiseScale*this.flip;
			this.vel.x = cos(angle);
			this.vel.y = sin(angle);
			this.vel.mult(simulationSpeed);
			this.pos.add(this.vel);
			--iterations;
		}
	}

	checkEdge(){
		if(this.pos.x > width || this.pos.x < 0 || this.pos.y > height || this.pos.y < 0){
			this.respawn();
		}
	}
	
	respawn(){
		this.pos.x = random(0, width);
		this.pos.y = random(0, height);
		this.life = maxLife;
		this.setColor();
	}

	display(r){
		ellipse(this.pos.x, this.pos.y, r, r);
	}
}

function advanceVisual()
{
	
	background(backgroundColor);
	for(var i = 0; i < nums; i++){
		particles[i].respawn();
		particles[i].life = random(0,maxLife);
  }
}