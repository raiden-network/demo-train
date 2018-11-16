import controlP5.*;

ControlP5 cp5;

Accordion accordion;

// Constantss
int Y_AXIS = 1;
int X_AXIS = 2;
color b1, b2, c1, c2, r1,
color0;
color[] colors;
PShape s;

void setup() {
  //size(640, 360,P2D);
  fullScreen(P3D);
  background(0);

  // Define colors
  b1 = color(255);
  b2 = color(0);
  c1 = color(204, 102, 0);
  c2 = color(0, 102, 153);
  colors = new color[8];
  colors[0] = color(204,0,215);
  colors[1] = color(#3bfa96);
  colors[2] = color(#f5ff3d);
  colors[3] = color(#02d9ff);
  
  colors[4] = color(#3bfa96);
  colors[5] = color(#f5ff3d);
  colors[6] = color(#02d9ff);
  colors[7] = color(#ffff03);
  r1=colors[int(random(7))];

  //noLoop();
  smooth();
  gui();
}

void draw() {
  // Background
  //setGradient(0, 0, width/2, height, b1, b2, X_AXIS);
  //setGradient(width/2, 0, width/2, height, b2, b1, X_AXIS);
  // Foreground
  //setGradient(50, 90, 540, 80, c1, c2, Y_AXIS);
  //setGradient(50, 190, 540, 80, c2, c1, X_AXIS);


  
}

void drawMountain(float r_stepsize, float r_jitter, float t_stepsize, float strokew,float t_min, float t_max, float rad_min, float rad_max) { 
  pushMatrix();
    translate(width/2., height/2.);
    float r_rand = random(r_jitter);
    PVector[] vs = generateRailLookUp(20);
    
    //outer loop creates radial virtual lines
    for (float r=0; r<TWO_PI;r+= r_stepsize + r_rand) {
      r_rand = random(r_jitter); 
      
      int rr = int(map(r,0,TWO_PI,0,vs.length));
      int rrr = int(map(r+r_stepsize+r_rand,0,TWO_PI,0,vs.length));
      
      
      float rad_rand = random(rad_min,rad_max);
      float t_rand = random(0.001, t_stepsize);
      
      //inner circle connects to radial lines
      for (float t=t_min; t<1; t+=t_rand) {
        float tt = map(t, t_min, 1, 0, t_max);
        stroke(lerpColor(b2,r1,tt));
        strokeWeight(strokew);
        // check if map(t,0,rad_rand,0,1) is faster
        
        //two circles in the middle
        //line(rad_rand*t*cos(r),rad_rand*t*sin(r),rad_rand*t*cos(r+r_stepsize+r_rand),rad_rand*t*sin(r+r_stepsize+r_rand));
          
        // racetrack shape
        if(rr<vs.length){
          //line(rad_rand*t*(vs[rr].x-width/2.),rad_rand*t*(vs[rr].y-height/2.),rad_rand*t*(vs[rr+1].x-width/2.),rad_rand*t*(vs[rr].x-width/2.));
          line(rad_rand*t*(vs[rr].x-width/2.),rad_rand*t*(vs[rr%vs.length].y-height/2.),rad_rand*t*(vs[rrr%vs.length].x-width/2.),rad_rand*t*(vs[rrr%vs.length].y-height/2.));
        }          
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


void gui() {
  
  cp5 = new ControlP5(this);
  
  
    Group g1 = cp5.addGroup("landscape params")
                .setBackgroundColor(color(0, 255))
                .setBackgroundHeight(150)
                ;
                
      cp5.addSlider("r_stepsize")
     .setPosition(60,20)
     .setSize(100,20)
     .setRange(0.01,1)
     .setValue(0.08)
     .moveTo(g1)
     ;
     
  cp5.addSlider("r_jitter")
     .setPosition(60,50)
     .setSize(100,20)
     .setRange(0.01,5)
     .setValue(0.1)
     .moveTo(g1)
     ; 
     
  cp5.addSlider("t_stepsize")
     .setPosition(60,80)
     .setSize(100,20)
     .setRange(0.00001,0.001)
     .setValue(0.001)
     .moveTo(g1)
     ; 
          
  cp5.addSlider("strokew")
     .setPosition(60,110)
     .setSize(100,20)
     .setRange(0.5,10)
     .setValue(1)
     .moveTo(g1)
     ; 
               
  cp5.addSlider("t_min")
     .setPosition(60,140)
     .setSize(100,20)
     .setRange(0.01,1)
     .setValue(0.3)
     .moveTo(g1)
     ;

  cp5.addSlider("t_max")
     .setPosition(60,170)
     .setSize(100,20)
     .setRange(0.01,5)
     .setValue(1)
     .moveTo(g1)
     ; 
                       
  cp5.addSlider("rad_min")
     .setPosition(60,200)
     .setSize(100,20)
     .setRange(1,20)
     .setValue(5.3)
     .moveTo(g1)
     ; 
                            
  cp5.addSlider("rad_max")
     .setPosition(60,230)
     .setSize(100,20)
     .setRange(1,20)
     .setValue(5.9)
     .moveTo(g1)
     ; 
     
  cp5.addBang("redraw")
     .setPosition(60,260)
     .setSize(100,20)
     .moveTo(g1)
     .plugTo(this,"drawM");
     ;
     
  accordion = cp5.addAccordion("acc")
                 .setPosition(40,40)
                 .setWidth(200)
                 .addItem(g1)
                 ;
                 
  accordion.setCollapseMode(Accordion.MULTI);
}

void drawM(){  float s1 = cp5.getController("r_stepsize").getValue();
  float s2 = cp5.getController("r_jitter").getValue();
  float s3 = cp5.getController("t_stepsize").getValue();
  float s4 = cp5.getController("strokew").getValue();
  float s5 = cp5.getController("t_min").getValue();
  float s8 = cp5.getController("t_min").getValue();
  float s6 = cp5.getController("rad_min").getValue();
  float s7 = cp5.getController("rad_max").getValue();
  background(0);
  //drawMountain(0.08,0.82,0.001,1,0.3,5.3,5.9);
  drawMountain(s1,s2,s3,s4,s5,s8,s6,s7); 
  vertexInterpolation();
}

  //drawMountain(0.08,0.82,0.001,1,0.3,5.3,5.9);
  //void drawMountain(float r_stepsize, float r_jitter, float t_stepsize, float strokew,float t_min, float rad_min, float rad_max) { 
