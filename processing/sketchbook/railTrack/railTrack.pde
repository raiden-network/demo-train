int numberOfSegments = 42; // resolution of track

int realNumberOfSegments;
int loopCounter = 0;
int oldLoopCounter = 1;
float railRadius = 630; // not global
float railLength = 1300; // no need to be global

PVector[] railSegmentsLookUp;

float trainPosition = 0; // in units of segments
float trainSpeed = 1.05; // in units of segments

int offsetStart = 60;

int xBarcode = 545;
int yBarcode = 1450;

final color redColor = color(255, 0, 0);
final color greenColor = color(0, 255, 0);

final int railJitter = 2;

int[] rs = {40,40,40,120, width, height,20,20,width,height,20,20};
int[] rands;

void setup(){
   fullScreen(P2D);
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
  background(0);
  drawLandscape();
  //drawMovingLandscape(true);
  //drawMiddleTree();
  clearRails();
  drawBarcode(xBarcode,yBarcode);
  drawTextBox(0,0);
}

void draw(){
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
    drawBarcode(xBarcode,yBarcode); 
  }
  
  //drawGlow(trainPosition/railSegmentsLookUp.length);
  // printMiddleTree();
  drawTrain(2, trainPosition + railSegmentsLookUp.length/2., 2);
  drawTrainText(1.6, trainPosition + railSegmentsLookUp.length/2.);

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

  return rvectors;
}

void drawRails(){
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
    printSeg(railSegmentsLookUp[segId].x, railSegmentsLookUp[segId].y, c, segId);   
  }
  endShape();
}

color getSegColor(float tp, float si){
    if(int(tp) < si){
      return greenColor;
    }
    else{
      return color(255, random(100), random(100));
    } 
}



void printSeg(float x, float y, color c, int id){
   
    color alphaColor = 5 << 030;  

    alphaColor = (75 + int(random(30))) << 030;
    stroke(c & ~#000000 | alphaColor);
    alphaColor = 25 << 030;
    
    strokeWeight(10+random(12));
    vertex(x+random(railJitter),y+random(railJitter));
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


void keyPressed(){
  float tmpTS = 0;
  if(keyCode == 139){
   trainSpeed += 0.01;
   println("speed me up: " + trainSpeed);
  }
  else if(keyCode == 140){
   trainSpeed -= 0.01;
   println("slow me down: " + trainSpeed);
  }
   else if(keyCode == 32){
   tmpTS = (((loopCounter - oldLoopCounter) / realNumberOfSegments) + trainSpeed);
  println(tmpTS);
     if(tmpTS > (trainSpeed - 0.3) && tmpTS < (trainSpeed + 0.3)){
     println("new train speed: " + trainSpeed);
     trainSpeed = tmpTS;
   }
   oldLoopCounter = loopCounter;
  }
  else{
   println(keyCode);
  }
}


void drawBarcode(int x, int y){
  //1320x400
  PImage img = loadImage("/home/train/demo-train/current_barcode.jpg");

  pushMatrix();
  translate(x,y);
  rotate(HALF_PI);

  noStroke();
  noFill();


  beginShape();
  texture(img);
  vertex(0, 0, 0, 0);
  vertex(465, 0, 1320, 0);
  vertex(465, 83, 1320, 400);
  vertex(0, 83, 0, 400);
  endShape();

  popMatrix();
}

void mouseClicked(){
  stroke(128);
  fill(128);
  textSize(30);
  String posi = "x: " + mouseX + "\ny: " + mouseY;
  println("x: " + mouseX + "\ny: " + mouseY);
  text(posi,mouseX,mouseY);

}

void drawTextBox(int x, int y){
  stroke(128);
  fill(128,12,43);
  textSize(50);
  text("TRAIN IS\nCOMING!",x,y);
}

void drawTrain(float scale, float tp, float range){
  PVector v;
  noFill();
  stroke(255,234,98,70);
  strokeWeight(4);
  float scale2 = scale - 0.4;
  
  beginShape();
    for(int i = int(sqrt((tp - range)*(tp - range)));  i < int(sqrt((tp + range)*(tp + range))); i++){
      //println(i);
      v = railSegmentsLookUp[i % railSegmentsLookUp.length];
      vertex(v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));  
    }
   endShape();
   
   v = railSegmentsLookUp[int(tp) % railSegmentsLookUp.length];
   line(v.x-scale2*(v.x-width/2.), v.y-scale2*(v.y-height/2.),v.x-scale*(v.x-width/2.), v.y-scale*(v.y-height/2.));
   
   fill(0);
   ellipse(v.x-scale2*(v.x-width/2.), v.y-scale2*(v.y-height/2.),70,50);
}


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
