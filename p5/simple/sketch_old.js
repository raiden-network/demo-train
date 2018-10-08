var trackShapeOuter;
var trackShapeInner;

class TrackOutline {
	constructor (xCenter, yCenter, xOffset, diameter, color) {
		this.xCenter = xCenter;
		this.yCenter = yCenter;
		this.xOffset = xOffset;
		this.circleDiameter = diameter;
		this.color = color;
	}
	
	draw () {
		noStroke();
		fill(this.color);
		ellipse(this.xCenter - this.xOffset, this.yCenter, this.circleDiameter, this.circleDiameter);
		ellipse(this.xCenter + this.xOffset, this.yCenter, this.circleDiameter, this.circleDiameter);
		rect(this.xCenter - this.xOffset, this.yCenter - this.circleDiameter/2, this.xOffset*2,this.circleDiameter);
	}
}


function setup() {
	noSmooth();
	var diameter = 400;
	var offset = 100;
	trackShapeOuter = new TrackOutline(windowWidth/2, windowHeight/2, offset, diameter, color(123,132,0,1));
	trackShapeInner = new TrackOutline(windowWidth/2, windowHeight/2, offset, diameter, color(219,211,73,1));
	createCanvas(windowWidth, windowHeight);
	background(200);
	

}


function draw() {
	// trackShapeOuter.draw();
	// trackShapeInner.draw();
	beginShape()
	ellipse(100,200,100,100);
	ellipse(100,100,200,200);
	endShape()
}
