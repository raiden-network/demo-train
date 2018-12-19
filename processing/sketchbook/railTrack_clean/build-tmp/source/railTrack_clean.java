import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class railTrack_clean extends PApplet {

int numberOfSegments = 42; // resolution of track
float railRadius = 200; // not global
float railLength = 300; // no need to be global

PVector[] railSegmentsLookUp;

float trainPosition = 0; // in units of segments
float trainSpeed = 0.95f; // in units of segments

int offsetStart = 60;

final int redColor = color(255, 0, 0);
final int greenColor = color(0, 255, 0);

final int railJitter = 2;

int[] rs = {40,40,40,120, width, height,20,20,width,height,20,20};
int[] rands;


public void setup(){
   
   //smooth(8);
   //size(1000,600);
   rs[4] = width;
   rs[5] = height;
   rs[8] = width;
   rs[9] = height;
   background(0);
   fill(100);
   stroke(100);
   noFill();
   strokeWeight(7);
   frameRate(15);
   
  railSegmentsLookUp = generateRailLookUp(numberOfSegments);
  drawLandscape();
  //drawMovingLandscape(true);
  drawMiddleTree();
  clearRails();
  drawBarcode(300,300);
}

public void draw(){
  trainPosition += trainSpeed;
  //println(frameRate);  
  //background(0);
  
  drawMiddleTree();
  clearRails();
  drawRails();
  
  // draw stuff once per circle
  if(trainPosition >= railSegmentsLookUp.length){
    trainPosition = 0;
    drawLandscape();
    drawMiddleTree();
    drawBarcode(300,300); 
  }
  
  //drawGlow(trainPosition/railSegmentsLookUp.length);
  // printMiddleTree();
  drawTrain(2, trainPosition + railSegmentsLookUp.length/2.f, 2);
  //drawTrainText(1.6, trainPosition + railSegmentsLookUp.length/2.);

}

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
  
  //println(stepsRatio);
  //println(stepsRad);
  //println(stepsStraight);
  
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


public void drawRails(){
    beginShape(QUAD_STRIP);
  //vertex(width/2.,height/2.);
  for(int segId = 0; segId < railSegmentsLookUp.length*0.83f; segId++){
    
    // begin new shape on train position
    if(PApplet.parseInt(trainPosition) == segId){
      endShape(); 
      //beginShape(QUAD_STRIP);
      beginShape(QUADS);
    }   
    int c = getSegColor(trainPosition, segId);
    printSeg(railSegmentsLookUp[segId].x, railSegmentsLookUp[segId].y, c, segId);   
  }
  endShape();
}

public int getSegColor(float tp, float si){
    if(PApplet.parseInt(tp) < si){
      return greenColor;
    }
    else{
      return color(255, random(100), random(100));
    } 
}


public void printSeg(float x, float y, int c, int id){
   
    int alphaColor = 5 << 030;  

    alphaColor = (75 + PApplet.parseInt(random(30))) << 030;
    stroke(c & ~0xff000000 | alphaColor);
    alphaColor = 25 << 030;
    
    strokeWeight(10+random(12));
    vertex(x+random(railJitter),y+random(railJitter));
}


public void drawMiddleTree(){
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
public void drawMovingLandscape(boolean init){
  noStroke();
  //strokeWeight(random(6));
  int r = PApplet.parseInt(random(255));
  int g = PApplet.parseInt(random(255));
  int b = PApplet.parseInt(random(255));
  //color col = color(r,g,b);
  
  
  
  
  if(init){
  rands = new int[PApplet.parseInt(random(1000))*rs.length];
    for(int i = 0; i < rands.length/rs.length; i+=rs.length){
      for(int j=0; j < rs.length; j++){
        rands[i+j] = PApplet.parseInt(random(rs[j]));
      }  
    }
  }
  else{
    
    for(int i = 0; i < rands.length; i++){
      rands[i]+=random(-2,4); 
    }
    
    for(int i = 0; i < rands.length/rs.length; i+=rs.length){
     fill(r+ rands[i+0],g + rands[i+1],b + rands[i+2],rands[i+3]);
     //stroke(r+ random(20),g + random(20),b + random(20));
     rect(rands[i+4],rands[i+5],rands[i+6],rands[i+7]);
     ellipse(rands[i+8],rands[i+9],rands[i+10],rands[i+11]);
    }
  }
  
}


public void clearRails(){
  noFill();
  stroke(0);
  strokeWeight(65);
  beginShape();
  for (PVector v : railSegmentsLookUp) {
    vertex(v.x, v.y);
  }
  vertex(railSegmentsLookUp[0].x,railSegmentsLookUp[0].y);
  endShape();
}

public void drawGlow(float scale){
  noFill();
  stroke(255,234,98,120);
  strokeWeight(7);
  
  beginShape();
    for (PVector v : railSegmentsLookUp) {
      vertex(v.x-scale*(v.x-width/2.f)*random(0.9f,1.1f), v.y-scale*(v.y-height/2.f)*random(0.9f,1.1f));
    }
    PVector vv = railSegmentsLookUp[0];
    vertex(vv.x-scale*(vv.x-width/2.f)*random(0.9f,1.1f), vv.y-scale*(vv.y-height/2.f)*random(0.9f,1.1f));
  endShape();
  
  stroke(255,234,98,73);
  strokeWeight(33);
  beginShape();
    scale *=random(0.9f,1.1f);
      for (PVector v : railSegmentsLookUp) {
      vertex(v.x-scale*(v.x-width/2.f), v.y-scale*(v.y-height/2.f));
    }
    vertex(vv.x-scale*(vv.x-width/2.f), vv.y-scale*(vv.y-height/2.f));
  endShape();
  
  stroke(255,234,98,24);
  strokeWeight(17);
  beginShape();
    scale *=2.6f;
      for (PVector v : railSegmentsLookUp) {
      vertex(v.x-scale*(v.x-width/2.f), v.y-scale*(v.y-height/2.f));
    }
    vertex(vv.x-scale*(vv.x-width/2.f), vv.y-scale*(vv.y-height/2.f));
  endShape();
}

public void drawGreen(){
  PVector vv = railSegmentsLookUp[0];
  beginShape();
    stroke(55,random(200,234),98,random(40,124));
    strokeWeight(17);
    float scale =6.6f;
      for (PVector v : railSegmentsLookUp) {
      scale = random(30);
      vertex(v.x-scale*(v.x-width/2.f), v.y-scale*(v.y-height/2.f));
    }
    vertex(vv.x-scale*(vv.x-width/2.f), vv.y-scale*(vv.y-height/2.f));
  endShape();
}

public void drawBarcode(int x, int y){
  //1320x400 
  PImage img = loadImage("../../current_barcode.jpg");
  
  pushMatrix();
  translate(x,y);
  rotate(HALF_PI);
  
  noStroke();
  noFill();
  
  beginShape();
  texture(img);
  vertex(0, 0, 200, 0);
  vertex(400, 0, 1120, 0);
  vertex(400, 100, 1120, 400);
  vertex(0, 100, 200, 400);
  endShape();
 
  popMatrix();
}


public void drawTrain(float scale, float tp, float range){
  PVector v;
  noFill();
  stroke(255,234,98,70);
  strokeWeight(4);
  float scale2 = scale - 0.4f;
  
  beginShape();
    for(int i = PApplet.parseInt(sqrt((tp - range)*(tp - range)));  i < PApplet.parseInt(sqrt((tp + range)*(tp + range))); i++){
      //println(i);
      v = railSegmentsLookUp[i % railSegmentsLookUp.length];
      vertex(v.x-scale*(v.x-width/2.f), v.y-scale*(v.y-height/2.f));  
    }
   endShape();
   
   v = railSegmentsLookUp[PApplet.parseInt(tp) % railSegmentsLookUp.length];
   line(v.x-scale2*(v.x-width/2.f), v.y-scale2*(v.y-height/2.f),v.x-scale*(v.x-width/2.f), v.y-scale*(v.y-height/2.f));
   
   fill(0);
   ellipse(v.x-scale2*(v.x-width/2.f), v.y-scale2*(v.y-height/2.f),70,50);
}


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
  public void settings() {  fullScreen(P3D); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "railTrack_clean" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
