int numberOfSegments = 42; // resolution of track
float railRadius = 200; // not global
float railLength = 300; // no need to be global

PVector[] railSegmentsLookUp;

float trainPosition = 0; // in units of segments
float trainSpeed = 0.15; // in units of segments

int offsetStart = 60;

final color redColor = color(255, 0, 0);
final color greenColor = color(0, 255, 0);

final int railJitter = 2;

int[] rs = {40,40,40,120, width, height,20,20,width,height,20,20};
int[] rands;

void setup(){
   fullScreen(P2D);
   smooth(8);
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
  drawBarcode();
}

void draw(){
  
  //background(0);
  clearRails();
  drawMiddleTree();
  println(frameRate);
  
  trainPosition += trainSpeed;


  beginShape(QUAD_STRIP);
  //vertex(width/2.,height/2.);
  for(int segId = 0; segId < railSegmentsLookUp.length*0.83; segId++){
    
    // begin new shape on train position
    if(int(trainPosition) == segId){
      endShape(); 
      //beginShape(QUAD_STRIP);
      beginShape(QUADS);
    }
    
    int c = getSegColor(trainPosition, segId);
    printSeg(railSegmentsLookUp[segId].x, railSegmentsLookUp[segId].y, c);
    
    
  }
  //vertex(width/2.,height/2.);
  endShape();
  //drawMovingLandscape(false);
  //drawMiddleTree();
  // keep train position circular
  if(trainPosition >= railSegmentsLookUp.length){
    trainPosition = 0;
    //background(0);
    drawLandscape();
    //drawMovingLandscape(true);
    drawMiddleTree();
    //drawGreen();
    drawBarcode();
    
  }
//drawGlow(trainPosition/railSegmentsLookUp.length);
  // printMiddleTree();

}

PVector[] generateRailLookUp(int numberOfSegs){
  // function to generate array of vectors along the track
  // specialized to racetrack-shape
  // coordinates are just generated for half the track and 
  // the rest is obtained by point reflection
  
  //calculate ratios in length between different segments
  float stepsRatio = railLength / railRadius / PI ;
  int stepsRad = int(numberOfSegs);
  int stepsStraight = int(numberOfSegs * stepsRatio);
  float temp_x = 0;
  float temp_y = 0;
  
  //println(stepsRatio);
  //println(stepsRad);
  //println(stepsStraight);
  
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
 
  return rvectors;
}



color getSegColor(float tp, float si){
    if(int(tp) < si){
      //stroke(greenColor & ~#000000); // green
      //fill(12,144,63,70); // green
      return greenColor;
    }
    else{
      //stroke(redColor & ~#000000); // red
      //fill(182,34,63,10); // red
      // noStroke();
      // noFill();
      // return redColor;
      return color(255, random(100), random(100));
    } 
}


void printSeg(float x, float y, color c){
    //noFill();
    //point(x, y);
    
    color alphaColor = 5 << 030;
    //fill(c & ~#000000 | alphaColor);
    //noStroke();
    //ellipse(x, y,55,55);
    
    
    //alphaColor = 25 << 030;
    //fill(c & ~#000000 | alphaColor);
    //noStroke();
    //ellipse(x, y,25,25);


    //alphaColor = 150 << 030;
    //fill(c & ~#000000 | alphaColor);
    //strokeWeight(1);
    //rect(x, y,2,2);
    

    alphaColor = (75 + int(random(30))) << 030;
    stroke(c & ~#000000 | alphaColor);
    alphaColor = 25 << 030;
    //fill(c & ~#000000 | alphaColor);
    
    strokeWeight(10+random(12));
    vertex(x+random(railJitter),y+random(railJitter));
    
    //alphaColor = 115 << 030;
    //stroke(c & ~#000000 | alphaColor);
    //strokeWeight(1);
    //noFill();
    //vertex(x+random(railJitter),y+random(railJitter));    
    //strokeWeight(1);
    //noStroke();
    //ellipse(x, y,10,10);
}


void drawMiddleTree(){
  //PImage img = loadImage("tree-network.jpg");
  //noStroke();
  //beginShape();
  //texture(img);

  //vertex(10+random(railJitter), 20, 0, 0);
  //vertex(80+random(railJitter), 5, 400, 0);
  //vertex(95+random(railJitter), 90, 400, 400);
  //vertex(40+random(railJitter), 95, 0, 400);
  //endShape();
  

  
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

void drawLandscape(){
  noStroke();
  //strokeWeight(random(6));
  int r = int(random(255));
  int g = int(random(255));
  int b = int(random(255));
  int siz = int(random(800));
  for(int i = 0; i < random(1000); i++){
   fill(r+ random(40),g + random(40),b + random(40),random(120));
   //stroke(r+ random(20),g + random(20),b + random(20));
   rect(random(width),random(height),siz + random(20),siz + random(20));
   ellipse(random(width),random(height),siz + random(20),siz + random(20));
  }
  
}
void drawMovingLandscape(boolean init){
  noStroke();
  //strokeWeight(random(6));
  int r = int(random(255));
  int g = int(random(255));
  int b = int(random(255));
  //color col = color(r,g,b);
  
  
  
  
  if(init){
  rands = new int[int(random(1000))*rs.length];
    for(int i = 0; i < rands.length/rs.length; i+=rs.length){
      for(int j=0; j < rs.length; j++){
        rands[i+j] = int(random(rs[j]));
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


void clearRails(){
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

void drawGlow(float scale){
  
  //fill(55,234,8,random(33,120));
  stroke(255,234,98,120);
  strokeWeight(7);
  beginShape();
  for (PVector v : railSegmentsLookUp) {
    vertex(v.x-scale*(v.x-width/2.)*random(0.9,1.1), v.y-scale*(v.y-height/2.)*random(0.9,1.1));
  }
  //vertex(railSegmentsLookUp[0].x,railSegmentsLookUp[0].y);
  PVector vv = railSegmentsLookUp[0];
  vertex(vv.x-scale*(vv.x-width/2.)*random(0.9,1.1), vv.y-scale*(vv.y-height/2.)*random(0.9,1.1));
  endShape();
  
  noFill();
  stroke(255,234,98,73);
  strokeWeight(33);
  beginShape();
  scale *=random(0.9,1.1);
    for (PVector v : railSegmentsLookUp) {
    vertex(v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));
  }
  //vertex(railSegmentsLookUp[0].x,railSegmentsLookUp[0].y);
  vertex(vv.x-scale*(vv.x-width/2.), vv.y-scale*(vv.y-height/2.));
  endShape();
  
  stroke(255,234,98,24);
  strokeWeight(17);
  beginShape();
  scale *=2.6;
    for (PVector v : railSegmentsLookUp) {
    vertex(v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));
  }
  vertex(vv.x-scale*(vv.x-width/2.), vv.y-scale*(vv.y-height/2.));
  endShape();
}

void drawGreen(){
  PVector vv = railSegmentsLookUp[0];
    beginShape();
      stroke(55,random(200,234),98,random(40,124));
  strokeWeight(17);
  float scale =6.6;
    for (PVector v : railSegmentsLookUp) {
    scale = random(30);
    vertex(v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));
  }
  vertex(vv.x-scale*(vv.x-width/2.), vv.y-scale*(vv.y-height/2.));
  endShape();
}

void drawBarcode(){
  //1320x400
  PImage img = loadImage("../../current_barcode.jpg");
  
  pushMatrix();
  translate(300,300);
  rotate(PI);
  
  noStroke();
  noFill();
  

  beginShape();
  texture(img);
  vertex(0, 0, 0, 0);
  vertex(100, 0, 1320, 0);
  vertex(100, 100, 1320, 400);
  vertex(0, 100, 0, 400);
  endShape();
 
  popMatrix();
}
