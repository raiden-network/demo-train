// Constantss
int Y_AXIS = 1;
int X_AXIS = 2;
color b1, b2, c1, c2, r1;
PShape s;

void setup() {
  size(640, 360,P2D);
  background(0);

  // Define colors
  b1 = color(255);
  b2 = color(0);
  c1 = color(204, 102, 0);
  c2 = color(0, 102, 153);
  r1 = color(random(255),random(255),random(255),random(255));

  noLoop();
}

void draw() {
  // Background
  //setGradient(0, 0, width/2, height, b1, b2, X_AXIS);
  //setGradient(width/2, 0, width/2, height, b2, b1, X_AXIS);
  // Foreground
  //setGradient(50, 90, 540, 80, c1, c2, Y_AXIS);
  //setGradient(50, 190, 540, 80, c2, c1, X_AXIS);
  drawMountain(0.05,0.1,0.03,5,0.4,1,3);
  vertexInterpolation();
  
}

void drawMountain(float r_stepsize, float r_jitter, float t_stepsize, int strokew,float t_min, int rad_min, int rad_max) { 
  pushMatrix();
    translate(width/2., height/2.);
    float r_rand = random(r_jitter);
    PVector[] vs = generateRailLookUp(100);
    
    //outer loop creates radial virtual lines
    for (float r=0; r<TWO_PI;r+= r_stepsize + r_rand) {
      r_rand = random(r_jitter); 
      
      int rr = int(map(r,0,TWO_PI,0,vs.length));
      
      float rad_rand = random(rad_min,rad_max);
      float t_rand = random(0.001, t_stepsize);
      
      //inner circle connects to radial lines
      for (float t=t_min; t<1; t+=t_rand) {
        float tt = map(t, t_min, 1, 0, 1);
        stroke(lerpColor(b2,r1,tt));
        strokeWeight(strokew);
        // check if map(t,0,rad_rand,0,1) is faster
        
        //two circles in the middle
        //line(rad_rand*t*cos(r),rad_rand*t*sin(r),rad_rand*t*cos(r+r_stepsize+r_rand),rad_rand*t*sin(r+r_stepsize+r_rand));
          
        // racetrack shape            
        line(rad_rand*t*(vs[rr].x-width/2.),rad_rand*t*(vs[rr].y-height/2.),rad_rand*t*vs[rr+1].x,rad_rand*t*vs[rr+1].y);
                    
      } 
        //draw radial lines...looks shitty
        //stroke(0);
        //strokeWeight(0.1);
        //line(rad_rand*cos(r),rad_rand*sin(r),0,0); 
    }  
  popMatrix();
}

void vertexInterpolation()  {
  
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

PVector[] generateRailLookUp(int numberOfSegs){
  // function to generate array of vectors along the track
  // specialized to racetrack-shape
  // coordinates are just generated for half the track and
  // the rest is obtained by point reflection

  //calculate ratios in length between different segments
  float railLength = 100;
  float railRadius = 50;
  float stepsRatio = railLength / railRadius / PI ;
  int stepsRad = int(numberOfSegs);
  int stepsStraight = int(numberOfSegs * stepsRatio);
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
