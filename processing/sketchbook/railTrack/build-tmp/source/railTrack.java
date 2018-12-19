import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import processing.net.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class railTrack extends PApplet {



// main program for demo-train visualisation

// press d while train is rollin to enable debug features
// global vars
  boolean debug = false;

  Client pyClient = new Client(this, "127.0.0.1", 5204);

  int numberOfSegments = 42; // resolution of track

  float screenScale = 2.f/3.f/2.f;

  int realNumberOfSegments;
  int loopCounter = 0;
  int oldLoopCounter = 1;
  float railRadius; 
  float railLength;

  PVector[] railSegmentsLookUp;

  float trainPosition; // in units of segments
  float trainSpeed = .01f;

  float railOffset = .84f; //starting point in percent of racetrack

  int xBarcode = PApplet.parseInt(545*screenScale);
  int yBarcode = PApplet.parseInt(1450*screenScale);

  int current_channel=0;
  int last_channel=0;


  final int redColor = color(255, 0, 0);
  final int greenColor = color(0, 255, 0);

  final int railJitter = 2;

  NetTopo topo = new NetTopo();
  TunnelLandscape land = new TunnelLandscape();
  TunnelLandscape landTopo = new TunnelLandscape();

public void setup(){
  
  //noSmooth();
  
  if(debug)println(displayWidth);
  // if(displayWidth>1440){
  //  railRadius = 630; // this is 
  //  railLength = 1300; // for the big screen
  // }
  // if(displayWidth>1000){
  //  railRadius = 315; // this is 
  //  railLength = 650; // for the big screen
  // }
  if(displayWidth>700){
   railRadius = 630*screenScale; // this is 
   railLength = 1300*screenScale; // for the big screen
  }
  else{
   railRadius = 330; // this is
   railLength = 500; // for the laptop screen
  }
  frameRate(25);
  railSegmentsLookUp = generateRailLookUp(numberOfSegments);

  topo.dsetup();
  land.tsetup();
  landTopo.tsetup();

  background(0);
}

public void draw(){
  if(!pyClient.active()&&debug){
    textSize(100);
    stroke(200,100,250);
    text("Client not active",width/2,height/2);
    pyClient = new Client(this, "127.0.0.1", 5204);
  }
  
  float trainP = (PApplet.parseInt((millis()-oldLoopCounter)*trainSpeed)%railSegmentsLookUp.length);
  
  readClient();
  clearRails();
  drawTrain(2, trainP, 12,30);
  drawRails(trainP);
  drawBarcode(xBarcode,yBarcode);

  //if(frameCount%50==0){
  //  drawTopologie(current_channel);
  //}

  if(debug){
  	println("frameRate: "+frameRate);
  }

}

// generate lookup-table for racetrack shaped rail-coordinates
public PVector[] generateRailLookUp(int numberOfSegs){
  // function to generate array of vectors along the track
  // specialized to racetrack-shape
  // coordinates are just generated for half the track and
  // the rest is obtained by point reflection
  //calculate ratios in length between different segments
  float stepsRatio = railLength / railRadius / PI ;
  int stepsRad = PApplet.parseInt(numberOfSegs);
  int stepsStraight = PApplet.parseInt(numberOfSegs * stepsRatio);
  float temp_x = 0;
  float temp_y = 0;

  realNumberOfSegments = 2 * (stepsRad + stepsStraight);

  PVector[] vectors = new PVector[2 * (stepsRad + stepsStraight)];
  PVector[] rvectors = new PVector[2 * (stepsRad + stepsStraight)];

  // fill straight parts
  for (int i = 0; i < stepsStraight; i++) {

    temp_x = width/2.f - railLength/2.f + i * (railLength/stepsStraight);
    temp_y = railRadius + height/2.f;

    vectors[i] = new PVector(temp_x,temp_y);
    vectors[i + vectors.length/2] = new PVector(width - temp_x, height - temp_y);
  }

  // fill curved parts
  for (int i = 0; i < stepsRad; i++) {

    temp_x = sin(PI/stepsRad * i) * railRadius + width/2.f + railLength/2.f;
    temp_y = cos(PI/stepsRad * i) * railRadius + height/2.f;

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
  int tmp_offset = PApplet.parseInt(railOffset*tmp_len);

  for(int i = 0; i<tmp_len; i++){
    tmp_vecs[i] = rvectors[(i+tmp_offset)%tmp_len];
  }

  return tmp_vecs;
}

public void drawRails(float tp){
  //float tp = (int((millis()-oldLoopCounter)*trainSpeed)%realNumberOfSegments);
    beginShape(QUAD_STRIP);
  //vertex(width/2.,height/2.);
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
public int getSegColor(float tp, float si){
    if(PApplet.parseInt(tp) < si){
      return greenColor;
    }
    else{
      return color(255, random(100), random(100));
    } 
}

// print rail segments
public void printSeg(float x, float y, int c, int id){
   
    int alphaColor = 5 << 030;  

    alphaColor = (75 + PApplet.parseInt(random(30))) << 030;
    stroke(c & ~0xff000000 | alphaColor);
    alphaColor = 25 << 030;
    
    strokeWeight(10+random(12));
    vertex(x+random(railJitter),y+random(railJitter));
}


public void clearRails(){
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

public void clearInnerRegion(){
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

// old landscape generator
public void drawLandscape(){
  noStroke();
  //strokeWeight(random(6));
  int r = PApplet.parseInt(random(255));
  int g = PApplet.parseInt(random(255));
  int b = PApplet.parseInt(random(255));
  int siz = PApplet.parseInt(random(800));
  for(int i = 0; i < random(1000); i++){
   fill(r+ random(40),g + random(40),b + random(40),random(120));
   //stroke(r+ random(20),g + random(20),b + random(20));
   rect(random(width),random(height),siz + random(20),siz + random(20));
   ellipse(random(width),random(height),siz + random(20),siz + random(20));
  }
}

// clear region below the rails

// calculate speed from trigger and set it
public void setTrainSpeed(){
  float tmpTS = 0;
  loopCounter=millis();
  //tmpTS = (((loopCounter - oldLoopCounter) / realNumberOfSegments /frameRate/2.) + trainSpeed)/2.;
  tmpTS = ((1.f * realNumberOfSegments / (loopCounter - oldLoopCounter)));
  if(debug)println(tmpTS);
     if(tmpTS > (trainSpeed - 10.3f) && tmpTS < (trainSpeed + 10.3f)){
     if(debug)println("new train speed: " + trainSpeed);
     trainSpeed = tmpTS;
     
   }
   if(debug)println(oldLoopCounter);
   if(debug)println(loopCounter);
   oldLoopCounter = loopCounter;
}

public void drawBarcode(int x, int y){
  //1320x400
  // PImage img = loadImage("/home/train/demo-train/current_barcode.jpg");
  PImage img = loadImage("../../../current_barcode.jpg");

  pushMatrix();
  translate(x,y);
  rotate(HALF_PI);

  noStroke();
  noFill();

  image(img,0,0,465*screenScale,83*screenScale);

  // beginShape();
  // texture(img);
  // vertex(0, 0, 0, 0);
  // vertex(465, 0, 1320, 0);
  // vertex(465, 83, 1320, 400);
  // vertex(0, 83, 0, 400);
  // endShape();

  popMatrix();
}

// draw textbox that is following the train
public void drawTextBox(int x, int y){
  stroke(128);
  fill(128,12,43);
  textSize(50);
  text("TRAIN IS\nCOMING!",x,y);
}

// draw something below the train
public void drawTrain(float scale, float tp, float range, float sw){
    

	PVector v;
	noFill();
	stroke(255,234,240,210);
	strokeWeight(sw);
	float scale2 = scale - 0.4f;

	beginShape();
	for(int i = PApplet.parseInt(sqrt((tp - range)*(tp - range)));  i < PApplet.parseInt(sqrt((tp + range)*(tp + range))); i+=6){
	  v = railSegmentsLookUp[(i+railSegmentsLookUp.length/2) % railSegmentsLookUp.length];
	  strokeWeight(sw+random(10));
	  vertex(v.x-scale*(v.x-width/2.f), v.y-scale*(v.y-height/2.f));  
	}
	endShape();

	// v = railSegmentsLookUp[int(tp) % railSegmentsLookUp.length];
	// line(v.x-scale2*(v.x-width/2.), v.y-scale2*(v.y-height/2.),v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));

	// fill(0);
	// ellipse(v.x-scale2*(v.x-width/2.), v.y-scale2*(v.y-height/2.),70,50);
}

// draw text that follows the train
public void drawTrainText(float scale, float tp){
  PVector v;
  textMode(SHAPE);
  textAlign(CENTER, CENTER);
  textSize(22);
  fill(255,234,98,70);
  noStroke();
  
  v = railSegmentsLookUp[PApplet.parseInt(tp) % railSegmentsLookUp.length];
  text(PApplet.parseInt(trainPosition), v.x-scale*(v.x-width/2.f), v.y-scale*(v.y-height/2.f)); 
}

// draw network topologie in inner region
public void drawTopologie(int pch){
  int xoff = -50;
  int yoff = 0;
  //topo.topoSizex = 600;
  //topo.topoSizey = 900;
  pushMatrix();
    translate(width/2-topo.topoSizex/2 + xoff,height/2-topo.topoSizey/2 + yoff);
    topo.ddraw(pch);
  popMatrix();
  //text()
}

// receive stuff from backend and call functions
public void readClient(){
  textSize(30);
  fill(200,100);
  
  char c = pyClient.readChar();
  if(PApplet.parseInt(c)!=65535){
    if(debug)println("received something from backend: "+c);
    //text("backend says: "+c, width/5., height*2/5.);
  }
  switch(c){
  case 't': 
    //println("train passed by");
    if(debug)text("tell me why\nthe train passed by", width/4.f, height/2);
    setTrainSpeed();
    break;
  case 's': 
    if(debug)println("let the show begin");
    background(246,102,205);
    textSize(30);
    stroke(0);
    fill(0);
    text("INIT", width/2.f, height/2);
    drawBarcode(xBarcode,yBarcode);
    break;
   case 'p': 
    if(debug)println("received payment");
    drawBarcode(xBarcode,yBarcode); 
    break;
   case 'm': 
    if(debug)println("a payment is missing");
    break;
  default:
    int n = PApplet.parseInt(c) - 48;
    if(n < 7){
    current_channel = n;
     if(debug)println("receiver " + n + " will get paid"); 
     text("receiver " + current_channel + "\nwill get paid", width/4.f, height/2);
     background(0);
     land.drawMountain(0.29f,0.15f,0.0094f,6.88f,0.48f,1.f,26.73f,29.07f,current_channel);
     clearInnerRegion();
     drawTopologie(current_channel%7);
     break;
    }
  
  } 
}

// some debug mouse functionality
public void mouseClicked(){
  stroke(128);
  fill(128);
  textSize(30);
  String posi = "x: " + mouseX + "\ny: " + mouseY;
  if(debug)println("x: " + mouseX + "\ny: " + mouseY);
  if(debug)text(posi,mouseX,mouseY);
}

// some debug mouise functionality
public void keyPressed(){
  
  if(keyCode == 139){
   trainSpeed += 0.01f;
   if(debug)println("speed me up: " + trainSpeed);
  }
  else if(keyCode == 140){
   trainSpeed -= 0.01f;
   if(debug)println("slow me down: " + trainSpeed);
  }
  else if(keyCode == 68){
    debug = !debug;
  }
   else if(keyCode == 32){
    background(0);
    setTrainSpeed();
    current_channel = PApplet.parseInt(random(7))+1;
    if(displayWidth>1440){
      land.drawMountain(0.29f,0.15f,9.4f,6.88f,0.48f,1.f,26.73f,29.07f,current_channel);
    }else{
      land.drawMountain(0.29f,0.15f,11,.6f,0.48f,1.f,10,12,current_channel);      
    }
    drawBarcode(xBarcode,yBarcode);
    drawTopologie(current_channel);
   }
  else{
   if(debug)println(keyCode);
  }
}
// An object that wraps the PShape

class Wiggler {
  
  // The PShape to be "wiggled"
  PShape s;
  // Its location
  float x, y;
  
  String name;
  
  // For 2D Perlin noise
  float yoff = 0;
  
  // We are using an ArrayList to keep a duplicate copy
  // of vertices original locations.
  ArrayList<PVector> original;
  
  int col = color(245,234,189,145);

  Wiggler(int xx, int yy, int mult, String n) {
    x = xx;
    y = yy; 
    name = n;

    // The "original" locations of the vertices make up a circle
    original = new ArrayList<PVector>();
    for (float a = 0; a < TWO_PI; a+=0.2f) {
      PVector v = PVector.fromAngle(a);
      v.mult(mult);
      original.add(v);
    }
    
    // Now make the PShape with those vertices
    s = createShape();
    s.beginShape();
    s.fill(col);
    //s.stroke(255,70);
    s.strokeWeight(1);
    for (PVector v : original) {
      s.vertex(v.x, v.y);
    }
    s.endShape(CLOSE);
  }

  public void wiggle() {
    
    float xoff = 0;
    // Apply an offset to each vertex
    for (int i = 0; i < s.getVertexCount(); i++) {
      // Calculate a new vertex location based on noise around "original" location
      PVector pos = original.get(i);
      float a = TWO_PI*noise(xoff,yoff);
      PVector r = PVector.fromAngle(a);
      r.mult(1.5f);
      r.add(pos);
      // Set the location of each vertex to the new one
      s.setVertex(i, r.x, r.y);
      // increment perlin noise x value
      xoff+= 0.5f;
    }
    // Increment perlin noise y value
    yoff += 0.02f;
  }

  public void display() {
    pushMatrix();
    pushMatrix();
    translate(x+random(2), y+random(2));
    shape(s);
    popMatrix();
  }
  
  public void texto(){
    fill(255,10);
    textSize(90);
    //textMode(CENTER);
    text(name,x+14,y+23);
    fill(255,30);
    textSize(95);
    //textMode(CENTER);
    text("R"+name,x-14,y+27);
        fill(255,65);
    textSize(55);
    //textMode(CENTER);
    text(name,x+34,y+23);
}
    
  public void setColor(int c){  
    s.setFill(c);
  }
}
//import processing.net.*; 


//class PyClient{
//  Client myClient = new Client(this.parent, "127.0.0.1", 5203); ;
//  int i = 0;
//  void PyClient() {  
//  } 
  
//  void ddraw() { 
//    i++;
//    myClient.write("raiden train rolls in"+i); // send whatever you need to send here
//    println(myClient.readChar());
//  } 
//}
class TunnelLandscape{
  // Constantss
  int Y_AXIS = 1;
  int X_AXIS = 2;
  int b1, b2, c1, c2, r1,
  color0;
  int[] colors;
  PShape s;
  PVector[] vs;
  
  public void tsetup() {
    //size(640, 360,P2D);
    background(0);

    vs = generateRailLookUp(20);
    
    // Define colors
    b1 = color(255);
    b2 = color(0);
    c1 = color(204, 102, 0);
    c2 = color(0, 102, 153);
    colors = new int[8];
    // colors[0] = color(#ffffff); //white
    // colors[1] = color(#808000); //olive
    // colors[2] = color(#ffe119); //gelb
    // colors[3] = color(#bfef45); //lime
    // colors[4] = color(#42d4f4); //cyan
    // colors[5] = color(#f032e6); //magenta
    // colors[6] = color(#911eb4); //purple
    // colors[7] = color(#f58231); //orange
    r1=colors[PApplet.parseInt(random(7))]; //what is this shit?

    // Blau=#0066DD
    // Türkis = #00DDCC
    // Grün = #BBDD00
    // Orange = #DDBB00
    // Rot = #DD1100
    // Pink = #DD00AA

    colors[0] = color(0xffBBBBBB); 
    colors[1] = color(0xff0066DD); 
    colors[2] = color(0xff00DDCC); 
    colors[3] = color(0xffBBDD00); 
    colors[4] = color(0xffDDBB00); 
    colors[5] = color(0xffDD1100); 
    colors[6] = color(0xffDD00AA); 
    colors[7] = color(0xffDD00AA); 
  
    //noLoop();
  }
  
  
  public void drawMountain(float r_stepsize, float r_jitter, float t_stepsize, float strokew,float t_min,float t_max, float rad_min, float rad_max, int colorId) { 
    //  rectMode(CENTER);
    //  noFill();
    //  stroke(colors[colorId]);
    //  strokeWeight(10);
    //  rect(width/2,height/2,width,height);
    
    // // strange shit. but this fixed the alignment
    // pushMatrix();
    //   translate(width/2, height/2);
    // popMatrix();
    
    pushMatrix();
    pushMatrix();
      translate(displayWidth/2, displayHeight/2);
      //translate(0,height/2+130);
      //translate(width/2, 0);

      float r_rand = random(r_jitter);
      t_stepsize/=100000;
      
      //outer loop creates radial virtual lines
      for (float r=0; r<TWO_PI;r+= r_stepsize + r_rand) {
        r_rand = random(r_jitter); 
        
        int rr = PApplet.parseInt(map(r,0,TWO_PI,0,vs.length));
        int rrr = PApplet.parseInt(map(r+r_stepsize+r_rand,0,TWO_PI,0,vs.length));
        
        
        float rad_rand = random(rad_min,rad_max);
        float t_rand = random(0.001f, t_stepsize);
        
        //inner circle connects to radial lines
        for (float t=t_min; t<1; t+=t_rand) {
          float tt = map(t, t_min, 1, 0, 1);
          stroke(lerpColor(b2,colors[colorId%7],tt));
          strokeWeight(strokew);
          // check if map(t,0,rad_rand,0,1) is faster
          
          //two circles in the middle
          //line(rad_rand*t*cos(r),rad_rand*t*sin(r),rad_rand*t*cos(r+r_stepsize+r_rand),rad_rand*t*sin(r+r_stepsize+r_rand));
            
          // racetrack shape
          if(rr<vs.length){
            //line(rad_rand*t*(vs[rr].x-width/2.),rad_rand*t*(vs[rr].y-height/2.),rad_rand*t*(vs[rr+1].x-width/2.),rad_rand*t*(vs[rr].x-width/2.));

            line(rad_rand*t*(vs[rr].x-width/2.f),
              rad_rand*t*(vs[rr%vs.length].y-height/2.f),
              rad_rand*t*(vs[rrr%vs.length].x-width/2.f),
              rad_rand*t*(vs[rrr%vs.length].y-height/2.f));

          }          
        } 
          //draw radial lines...looks shitty
          //stroke(0);
          //strokeWeight(0.1);
          //line(rad_rand*cos(r),rad_rand*sin(r),0,0); 
      }  
    popMatrix();
    popMatrix();
  }
  
  public void vertexInterpolation()  {
    
    stroke(255);
    strokeWeight(2);
    noFill();
    s = createShape();
    s.beginShape();
    s.vertex(0,0);
      //s.bezierVertex(80, 0, 80, 75, 30, 75);
      //s.bezierVertex(50, 80, 60, 25, 30, 20);
    s.curveVertex(0,0);
    s.curveVertex(0,0);
    s.curveVertex(100,0);
    s.curveVertex(200,0);
    s.curveVertex(250,0);
    s.curveVertex(250,0);
    s.vertex(0,0);
    s.endShape(CLOSE);
    shape(s);
  
    beginShape();
    fill(0);
    stroke(0);
    PVector[] vs = generateRailLookUp(100);
    for (PVector v: vs) {
      //point(v.x,v.y);
      vertex(v.x,v.y);
    }
    endShape();
  
  }
  
  public PVector[] generateRailLookUp(int numberOfSegs){
    // function to generate array of vectors along the track
    // specialized to racetrack-shape
    // coordinates are just generated for half the track and
    // the rest is obtained by point reflection
  
    //calculate ratios in length between different segments
    float railLength = 100;
    float railRadius = 50;
    float stepsRatio = railLength / railRadius / PI ;
    int stepsRad = PApplet.parseInt(numberOfSegs);
    int stepsStraight = PApplet.parseInt(numberOfSegs * stepsRatio);
    float temp_x = 0;
    float temp_y = 0;
  
    //println(stepsRatio);
    //println(stepsRad);
    //println(stepsStraight);
  
    int realNumberOfSegments = 2 * (stepsRad + stepsStraight);
  
    PVector[] vectors = new PVector[2 * (stepsRad + stepsStraight)];
    PVector[] rvectors = new PVector[2 * (stepsRad + stepsStraight)];
  
    // fill straight parts
    for (int i = 0; i < stepsStraight; i++) {
  
      temp_x = width/2.f - railLength/2.f + i * (railLength/stepsStraight);
      temp_y = railRadius + height/2.f;
  
      vectors[i] = new PVector(temp_x,temp_y);
      vectors[i + vectors.length/2] = new PVector(width - temp_x, height - temp_y);
    }
  
    // fill curved parts
    for (int i = 0; i < stepsRad; i++) {
  
      temp_x = sin(PI/stepsRad * i) * railRadius + width/2.f + railLength/2.f;
      temp_y = cos(PI/stepsRad * i) * railRadius + height/2.f;
  
      vectors[i + stepsStraight] = new PVector(temp_x,temp_y);
      vectors[i + stepsStraight + vectors.length/2] = new PVector(width - temp_x, height - temp_y);
    }
  
    //reverse array ;)
    for (int i = 0; i < vectors.length; i++) {
      rvectors[i] = vectors[vectors.length-i-1];
    }
  
    return rvectors;
}
}
/////////////////////////////////////////////
//this class generates the inner topologie//
///////////////////////////////////////////
class NetTopo{

  int[] colors = new int[8];
  int noKnots = 7;
  PVector[] vecs = new PVector[noKnots];
  // Wiggler[] wiggls = new Wiggler[noKnots];
  //TunnelLandscape[] tunnels = new TunnelLandscape[noKnots];
  int topoSizex = PApplet.parseInt(900*2/3.f);
  int topoSizey = PApplet.parseInt(900*2/3.f);
  int blobSize = topoSizex/18;
  int[][] channels = new int [noKnots][6];
  int[] ch0 = {0};
  int[] ch1 = {0,1,0};
  int[] ch2 = {0,1,2};
  int[] ch3 = {0,1,2,3};
  int[] ch4 = {0,1,4};
  int[] ch5 = {0,1,4,5};
  int[] ch6 = {0,1,6};  


  int col_higlight = color(30,123,34,230);

  NetTopo(){
    // no con =D
  }
  
  public void dsetup(){
  
  // this is fixed to 7 hardcoded channels
  // if more channels should be added this has be be redone
  channels[0] = ch0; 
  channels[1] = ch1;
  channels[2] = ch2;
  channels[3] = ch3;
  channels[4] = ch4; 
  channels[5] = ch5;
  channels[6] = ch6;

  colors[0]= color(0xffBBBBBB); 
  colors[1] = color(0xff0066DD); 
  colors[2] = color(0xff00DDCC); 
  colors[3] = color(0xffBBDD00); 
  colors[4] = color(0xffDDBB00); 
  colors[5] = color(0xffDD1100); 
  colors[6] = color(0xffDD00AA); 
  colors[7] = color(0xffDD00AA); 
  
   // the position of the blobs is also hardcoded below
   // but with respect to the overall size of the diagram
   // vertical positioning
   // vecs[6] = new PVector(topoSizex/5,topoSizey*2/7);
   // vecs[5] = new PVector(topoSizex/4,topoSizey*41/55);
   // vecs[4] = new PVector(topoSizex/3,topoSizey*8/15.);
   // vecs[3] = new PVector(topoSizex*22./33.,topoSizey*25./34.);
   // vecs[2] = new PVector(topoSizex*2./3.,topoSizey*8/15.);
   // vecs[1] = new PVector(topoSizex/2.,topoSizey*35./90.);
   // vecs[0] = new PVector(topoSizex/2.,topoSizey/7.);
   
   /*


        4 - 5
       /
  0 - 1 - 6
       \
        2 - 3   

   */


  //hotizontal positioning
  vecs[6] = new PVector(topoSizex*0.7f,topoSizey*0.5f);
  vecs[5] = new PVector(topoSizex*0.9f,topoSizey*0.33f);
  vecs[4] = new PVector(topoSizex*0.6f,topoSizey*0.33f);
  vecs[3] = new PVector(topoSizex*0.9f,topoSizey*0.66f);
  vecs[2] = new PVector(topoSizex*0.6f,topoSizey*0.66f);
  vecs[1] = new PVector(topoSizex*0.4f,topoSizey*0.5f);
  vecs[0] = new PVector(topoSizex*0.1f,topoSizey*0.5f);


  //  for(int i = 0; i < vecs.length; i++){
  //    wiggls[i] = new Wiggler(int(vecs[i].x), int(vecs[i].y),blobSize,str(i));
  //  }
  }
  
  public void ddraw(int current_channel){
    noFill();
    strokeWeight(2);
    stroke(245,221,225,80);
    for (int[] ch : channels){
      beginShape();
      for(int c : ch){
        vertex(vecs[c].x, vecs[c].y);
        // wiggls[c].setColor(color(200,40));
      }
      endShape();
    }
    
    highlightChannel(current_channel%noKnots);

    int _ch = 0;
    for (PVector pv : vecs){
      pushMatrix();
        translate(pv.x-width/2,pv.y-height/2);
          // void drawMountain(float r_stepsize, float r_jitter, float t_stepsize, float strokew,float t_min,float t_max, float rad_min, float rad_max, int colorId) 
        //landTopo.drawMountain(.1,.15,.1,9.04,0.28,1.,0.3,1.9,_ch%noKnots);
        //landTopo.drawMountain(.7,.55,.6,1,.98,1.,0.4,0.7,_ch%noKnots);
        //landTopo.drawMountain(.1,.15,.1,.04,.48,2.,0.8,0.95,_ch%noKnots);
        
  // void drawNode(float r_stepsize, float r_jitter, float t_stepsize, float strokew,float t_min, float rad_min, float rad_max, int colorId) { 

        drawNode(.1f,.15f,.1f,.04f,0.48f,45.f,48.f,_ch);
        translate(width/2,height/2);
        texto(_ch,current_channel);
        _ch++;
      popMatrix();
    }
    
    // for (Wiggler w : wiggls){
    //    // w.display();
    //    // w.wiggle();
    //    //w.texto();
    // }
 }
  
  public void highlightChannel(int ch){
      strokeWeight(14);
      stroke(col_higlight);
      noFill();
      //fill(3,73,4,30);
      beginShape();
        for(int c : channels[ch]){
          vertex(vecs[c].x, vecs[c].y);
          // wiggls[c].setColor(color(6,250,10,40));
        }
      endShape();

      noStroke();
      //fill(3,25,4,30);
      beginShape();
        for(int c : channels[ch]){
          ellipse(vecs[c].x, vecs[c].y,50,40);
          // wiggls[c].setColor(color(6,250,10,40));
        }
      endShape();

    
  }
  
  // void drawKnot(int x, int y, String name){
  // }

// print text next to the knots
// i see the irony in int name as well, but dgaf
    public void texto(int name, int current_channel){
    int xoff = 35;
    int yoff = -20;
    int xpitch = 0;
    int ypitch = 30;
    int _line = 0; // is there a convention to indicate counter vars??

    // underlying textbox
    fill(0,120);
    // stroke(#BBBBBB);
    // strokeWeight(.2);
    noStroke();
    if(name==current_channel){
      stroke(col_higlight);
      strokeWeight(2);
    }
    rect(xoff-10,yoff-30,90,70);

    fill(255,201);
    textSize(20);
    text("nø:",xoff, yoff + _line * ypitch);

    fill(255,201);
    textSize(30);
    text(name,xoff + 30, yoff + _line * ypitch);
    // fill(0,255);
    // textSize(tsize);
    // text(name,xoff, yoff + _line * ypitch);

    if(name==current_channel){
      _line++;
      fill(col_higlight);
      textSize(20);
      text("active",xoff, yoff + _line * ypitch);
    }
  }

  public void drawNode(float r_stepsize, float r_jitter, float t_stepsize, float strokew,float t_min, float rad_min, float rad_max, int colorId) { 
  pushMatrix();
  int b1 = color(255);
  int b2 = color(0);
  int c1 = color(204, 102, 0);
  int c2 = color(0, 102, 153);
  int r1 = color(random(255),random(255),random(255),random(255));

    translate(width/2.f, height/2.f);
    float r_rand = random(r_jitter);
    PVector[] vs = generateRailLookUp(100);
    t_stepsize/=100000;
    
    //outer loop creates radial virtual lines
    for (float r=0; r<TWO_PI;r+= r_stepsize + r_rand) {
      r_rand = random(r_jitter); 
      
      int rr = PApplet.parseInt(map(r,0,TWO_PI,0,vs.length));
      println(rr);
      
      float rad_rand = random(rad_min,rad_max);
      float t_rand = random(0.001f, t_stepsize);
      
      //inner circle connects to radial lines
      for (float t=t_min; t<1; t+=t_rand) {
        float tt = map(t, t_min, 1, 0, 1);
        stroke(lerpColor(b2,colors[colorId%7],tt));
        strokeWeight(strokew);
        // check if map(t,0,rad_rand,0,1) is faster
        
        //two circles in the middle
        line(rad_rand*t*cos(r),rad_rand*t*sin(r),rad_rand*t*cos(r+r_stepsize+r_rand),rad_rand*t*sin(r+r_stepsize+r_rand));
                    
        //line(rad_rand*t*vs[rr].x,rad_rand*t*vs[rr].y,rad_rand*t*vs[rr+1].x,rad_rand*t*vs[rr+1].y);
                    
      } 
        //draw radial lines...looks shitty
        //stroke(0);
        //strokeWeight(0.1);
        //line(rad_rand*cos(r),rad_rand*sin(r),0,0); 
    }  
  popMatrix();
}
}
  public void settings() {  fullScreen(FX2D);  smooth(8); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "railTrack" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
