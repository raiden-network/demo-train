int numberOfSegments = 64; // resolution of track
float railRadius = 200; // not global
float railLength = 300; // no need to be global

PVector[] railSegmentsLookUp;

float trainPosition = 0; // in units of segments
float trainSpeed = 0.5; // in units of segments

int offsetStart = 60;

final color redColor = color(255, 0, 0);
final color greenColor = color(0, 255, 0);


void setup(){
   fullScreen();
   //size(1000,600);
   background(0);
   fill(100);
   stroke(100);
   noFill();
   strokeWeight(7);

  railSegmentsLookUp = generateRailLookUp(numberOfSegments);
}

void draw(){
  
  background(0);
  
  trainPosition += trainSpeed;

  for(int segId = 0; segId < railSegmentsLookUp.length; segId++){
  
    int c = setSegColor(trainPosition, segId);
    printSeg(railSegmentsLookUp[segId].x, railSegmentsLookUp[segId].y, c);
  }
  
  // keep train position circular
  trainPosition %= railSegmentsLookUp.length; 
  // println(trainPosition);
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



color setSegColor(float tp, float si){
    if(tp < si){
      stroke(greenColor & ~#000000); // green
      fill(12,144,63,70); // green
      return greenColor;
    }
    else{
      stroke(redColor & ~#000000); // red
      fill(182,34,63,10); // red
      // noStroke();
      // noFill();
      return redColor;
    } 
}


void printSeg(float x, float y, color c){
    //noFill();
    //point(x, y);
    
    color alphaColor = 5 << 030;
    fill(c & ~#000000 | alphaColor);
    noStroke();
    ellipse(x, y,55,55);
    
    
    alphaColor = 25 << 030;
    fill(c & ~#000000 | alphaColor);
    noStroke();
    ellipse(x, y,25,25);


    alphaColor = 150 << 030;
    fill(c & ~#000000 | alphaColor);
    strokeWeight(1);
    rect(x, y,2,2);
    

    
    //strokeWeight(1);
    //noStroke();
    //ellipse(x, y,10,10);
}
