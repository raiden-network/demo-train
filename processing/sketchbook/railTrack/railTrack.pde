///////////////////////////////////////////////////
// main program for raiden demo-train visualisation
//
// press d while train is rollin to enable debug features
//////////////////////////////////////////////////

import processing.net.*;

// global vars
  boolean debug = false;

  Client pyClient = new Client(this, "127.0.0.1", 5204);

  int numberOfSegments = 82;      // resolution of track

  float screenScale = 2./3./2.;   // used to lower resolution

  int realNumberOfSegments;
  int loopCounter = 0;            // to evaluate train speed
  int oldLoopCounter = 1;
  float trainPosition;            // in units of segments
  float trainSpeed = .0229;
  float[] trainSpeeds = {trainSpeed,trainSpeed,trainSpeed};
  
  float railRadius;               // they are set in setup
  float railLength;               // according to resolution

  PVector[] railSegmentsLookUp;   // holds coordinates of track

  float railOffset = .90;         // where is the barrier (in %)

  int xBarcode = int(545*screenScale);  // position of barcode
  int yBarcode = int(1450*screenScale);

  int xPaymentTextbox = int(1100);  // position of info textbox
  int yPaymentTextbox = int(620);

  int current_channel = 0;        // active node

  int railJitter = 2;             // graphical jitter for rail segments

  NetTopo topo = new NetTopo();   // network-topologie visualizer
  TunnelLandscape land = new TunnelLandscape();  // background visualizer

// init
void setup(){
  fullScreen(FX2D);
  smooth(8);
  background(0);

  if(debug)println(displayWidth);

  if(displayWidth>700){               // change value accordingly
   railRadius = 630*screenScale;      // this is 
   railLength = 1300*screenScale;     // for the big screen
  }
  else{
   railRadius = 330;                  // this is
   railLength = 500;                  // for the laptop screen
  }
  frameRate(25);
  railSegmentsLookUp = generateRailLookUp(numberOfSegments);    //generate lookup-table

  topo.dsetup();
  land.tsetup();
}

// main loop
void draw(){ 
  float trainP = getTrainPosition();
   
  clearRails();
  //drawTrain(2, trainP, 5,42);       // draw train illuminations
  //drawTrain(2, trainP, 10,32);
  //drawTrain(2, trainP, 25,22);
  //drawTrain(2, trainP, 35,12);
  drawRails(trainP);                // animate the rails
  drawBarcode(xBarcode,yBarcode);

  if(frameCount%25 == 0){           // do this every 25 frames ~ 1 second


    steerFrontend();                // THIS IS THE MAIN CALL
    

    if(!pyClient.active()){       // restart client if not active
      pyClient = new Client(this, "127.0.0.1", 5204);
      if(debug){
        textSize(20);
        stroke(200,100,250);
        text("Client not active",width/2,height/2);
      }
    }
  }

  if(debug)println("frameRate: "+frameRate);

}

// decide what to do and call functions
void steerFrontend(){
  char backendResponse = readClient();
  switch(backendResponse){
  case 's':                                   // initialisation
    if(debug)println("let the show begin");
    background(246,102,205);
    textSize(30);
    stroke(0);
    fill(0);
    text("INIT", width/2., height/2);
    drawBarcode(xBarcode,yBarcode);
    break;
  case 't':                                   // distance-probe trigger
    if(debug)text("tell me why\nthe train passed by", width/4., height/2);
    setTrainSpeed();
    // newPaymentCredentials(xPaymentTextbox, yPaymentTextbox);
    break;
   case 'p':                                  // payment received
    if(debug)println("received payment");
    drawBarcode(xBarcode,yBarcode);
    break;
   case 'm':                                  // payment failed
    if(debug)println("a payment is missing");
    break;
   case 'x':
    break;
  default:                                    // select node
    int n = int(backendResponse) - 48;
    if(n < 7){
    current_channel = n;
     if(debug)println("receiver " + n + " will get paid"); 
     text("receiver " + current_channel + "\nwill get paid", width/4., height/2);
     drawLandscape();  
     drawTopologie(current_channel%7);
     break;
    }  
  } 
}

// function to generate array of vectors along the track
PVector[] generateRailLookUp(int numberOfSegs){
  // specialized to racetrack-shape
  // coordinates are just generated for half the track and
  // the rest is obtained by point reflection
  //calculate ratios in length between different segments
  float stepsRatio = railLength / railRadius / PI ;
  int stepsRad = int(numberOfSegs);
  int stepsStraight = int(numberOfSegs * stepsRatio);
  float temp_x = 0;
  float temp_y = 0;

  realNumberOfSegments = 2 * (stepsRad + stepsStraight);

  PVector[] vectors = new PVector[2 * (stepsRad + stepsStraight)];
  PVector[] rvectors = new PVector[2 * (stepsRad + stepsStraight)];

  // fill straight parts
  for (int i = 0; i < stepsStraight; i++) {

    temp_x = width/2. - railLength/2. + i * (railLength/stepsStraight);
    temp_y = railRadius + height/2.;

    vectors[i] = new PVector(temp_x,temp_y);
    vectors[i + vectors.length/2] = new PVector(width - temp_x, height - temp_y);
  }

  // fill curved parts
  for (int i = 0; i < stepsRad; i++) {

    temp_x = sin(PI/stepsRad * i) * railRadius + width/2. + railLength/2.;
    temp_y = cos(PI/stepsRad * i) * railRadius + height/2.;

    vectors[i + stepsStraight] = new PVector(temp_x,temp_y);
    vectors[i + stepsStraight + vectors.length/2] = new PVector(width - temp_x, height - temp_y);
  }

  //reverse array ;)
  for (int i = 0; i < vectors.length; i++) {
    rvectors[i] = vectors[vectors.length-i-1];
  }


  //rearrange array with offset
  int tmp_len = rvectors.length;
  PVector[] tmp_vecs = new PVector[tmp_len];
  int tmp_offset = int(railOffset*tmp_len);

  for(int i = 0; i<tmp_len; i++){
    tmp_vecs[i] = rvectors[(i+tmp_offset)%tmp_len];
  }

  return tmp_vecs;
}

// calculate speed from trigger and set it
void setTrainSpeed(){
  float tmpTS = 0;
  loopCounter=millis();
  //tmpTS = (((loopCounter - oldLoopCounter) / realNumberOfSegments /frameRate/2.) + trainSpeed)/2.;
  tmpTS = ((1. * railSegmentsLookUp.length / (loopCounter - oldLoopCounter)));
  if(debug)println("train speed current round: " + tmpTS);
  if(debug)println(tmpTS);
     //if(tmpTS > (trainSpeed - 0.01) && tmpTS < (trainSpeed + 0.01)){

     trainSpeeds[2]=trainSpeeds[1];
     trainSpeeds[1]=trainSpeeds[0];
     trainSpeeds[0]=tmpTS;

     trainSpeed = (trainSpeeds[0] + trainSpeeds[1] + trainSpeeds[2])/3.;
     // trainSpeed = 0.5;     


     if(debug){
      fill(255);
      println("new train speed accepted: " + trainSpeed);
      text("new train speed: " + trainSpeed, 100, 100);
     }
     
   //}
   if(debug)println(oldLoopCounter);
   if(debug)println(loopCounter);
   oldLoopCounter = loopCounter;
   // trainSpeed = 0.5;
}

// calculates position of train based on current speed and system-time
float getTrainPosition(){
  return (int((millis()-oldLoopCounter)*trainSpeed)%railSegmentsLookUp.length);
}

// call landscape generator with specific params
void drawLandscape(){
  background(0);
  land.drawMountain(0.29,0.15,11,.6,0.42,1.,10,12,current_channel);
}

void drawBarcode(int x, int y){
  //1320x400
  PImage img = loadImage("../../../current_barcode.jpg");

  pushMatrix();
  translate(x,y);
  rotate(HALF_PI);

  noStroke();
  noFill();

  image(img,0,0,465*screenScale,83*screenScale);
  popMatrix();
}

void newPaymentCredentials(int x, int y){
  stroke(128);
  fill(255,255,255);
  textSize(30);
  // rotate(HALF_PI);
  text("New Payment\n required", x, y);
}

// draw textbox that is following the train
void drawTextBox(int x, int y){
  stroke(128);
  fill(128,12,43);
  textSize(50);
  text("TRAIN IS\nCOMING!",x,y);
}

// draw something below the train
void drawTrain(float scale, float tp, float range, float sw){
	PVector v;
	noFill();
	float scale2 = scale - 0.4;

	stroke(255,234,240,50);
	strokeWeight(sw);

	beginShape();
		for(int i = int(sqrt((tp - range)*(tp - range)));  i < int(sqrt((tp + range)*(tp + range))); i+=3)
		{
		  v = railSegmentsLookUp[(i+railSegmentsLookUp.length/2) % railSegmentsLookUp.length];
		  strokeWeight(sw+random(1));
		  vertex(v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));  
		}
	endShape();


	// v = railSegmentsLookUp[int(tp) % railSegmentsLookUp.length];
	// line(v.x-scale2*(v.x-width/2.), v.y-scale2*(v.y-height/2.),v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));

	// fill(0);
	// ellipse(v.x-scale2*(v.x-width/2.), v.y-scale2*(v.y-height/2.),70,50);
}

// draw text that follows the train
void drawTrainText(float scale, float tp){
  PVector v;
  textMode(SHAPE);
  textAlign(CENTER, CENTER);
  textSize(22);
  fill(255,234,98,70);
  noStroke();
  
  v = railSegmentsLookUp[int(tp) % railSegmentsLookUp.length];
  text(int(trainPosition), v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.)); 
}

// draw network topologie in inner region
void drawTopologie(int pch){
  clearInnerRegion();
  
  int xoff = -50;
  int yoff = 0;
  
  pushMatrix();
    translate(width/2-topo.topoSizex/2 + xoff,height/2-topo.topoSizey/2 + yoff);
    topo.ddraw(pch);
  popMatrix();
}

// the whole track is drawn here
// it consists of multiple segments in two different colors 
// which are grouped in two shapes
void drawRails(float tp){
  beginShape(QUAD_STRIP);
  for(int segId = 0; segId < railSegmentsLookUp.length*1; segId++){  
    // begin new shape on train position
    if( tp == segId){
  endShape(); 
  //beginShape(QUAD_STRIP);
  beginShape(QUADS);
  }   
    int c = getSegColor(tp, segId);
    printSeg(railSegmentsLookUp[segId].x, railSegmentsLookUp[segId].y, c, segId);   
  }
  endShape();
}

// helper function for rail segments
// rail colors are defined here
color getSegColor(float tp, float si){
    if(int(tp) < si){
      return color(random(10), 255, random(10));
    }
    else{
      return color(255, random(100), random(100));
    } 
}

// print rail segments
void printSeg(float x, float y, color c, int id){
   
    color alphaColor = 5 << 030;  

    alphaColor = (75 + int(random(30))) << 030;
    stroke(c & ~#000000 | alphaColor);
    alphaColor = 25 << 030;
    
    strokeWeight(10+random(4));
    vertex(x+random(railJitter),y+random(railJitter));
}

// clear region below the rails
void clearRails(){
  noFill();
  stroke(0);
  strokeWeight(71);
  beginShape();
  for (PVector v : railSegmentsLookUp) {
    vertex(v.x, v.y);
  }
  vertex(railSegmentsLookUp[0].x,railSegmentsLookUp[0].y);
  endShape();
}

void clearInnerRegion(){
  fill(0);
  stroke(0);
  //strokeWeight(30);
  beginShape();
  vertex(railSegmentsLookUp[0].x,railSegmentsLookUp[0].y);
  for (PVector v : railSegmentsLookUp) {
    vertex(v.x, v.y);
  }
  vertex(railSegmentsLookUp[0].x,railSegmentsLookUp[0].y);
  endShape();
}

// receive stuff from backend
char readClient(){
  textSize(30);
  fill(200,100);
  
  char c = pyClient.readChar();
  println("(c): "+(c));
  if(int(c)!=65535){
    if(debug)println("received something from backend: "+c);
    return c;
  }
  else {
    return 'x';  
  }
}

// some debug mouse functionality
void mouseClicked(){
  stroke(128);
  fill(128);
  textSize(30);
  String posi = "x: " + mouseX + "\ny: " + mouseY;
  if(debug)println("x: " + mouseX + "\ny: " + mouseY);
  if(debug)text(posi,mouseX,mouseY);
}

// some debug functionality
void keyPressed(){
  
  if(keyCode == 43){
   trainSpeed += 0.01;
   if(debug)println("speed me up: " + trainSpeed);
  }
  else if(keyCode == 45){
   trainSpeed -= 0.01;
   if(debug)println("slow me down: " + trainSpeed);
  }
  else if(keyCode == 68){
    newPaymentCredentials(xPaymentTextbox, yPaymentTextbox);
    debug = !debug;
  }
   else if(keyCode == 32){
    background(0);
    setTrainSpeed();
    current_channel = int(random(6))+1;
    drawLandscape();
    drawBarcode(xBarcode,yBarcode);
    drawTopologie(current_channel);

   }
  else{
   if(debug)println(keyCode);
  }
}
