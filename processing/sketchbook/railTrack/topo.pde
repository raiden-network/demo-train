/////////////////////////////////////////////
//this class generates the inner topologie//
///////////////////////////////////////////
class NetTopo{

     /*


        4 - 5
       /
  0 - 1 - 6
       \
        2 - 3   

   */

  int noKnots = 7;
  float nodeRadius = 30;
  color[] colors = new color[noKnots];
  String[] nodeNames = new String[noKnots];
  PVector[] vecs = new PVector[noKnots];
  
  //CW from 3 in degrees
  float[] radialOffsets = {
                            180,
                            180,
                            235,
                            225,
                            225,
                            225,
                            225
                          };

  int topoSizex = int(900*2/3.);
  int topoSizey = int(900*2/3.);
  int blobSize = topoSizex/18;
  int[][] channels = new int [noKnots][6];
  int[] ch0 = {0};
  int[] ch1 = {0,1,1};
  int[] ch2 = {0,1,2};
  int[] ch3 = {0,1,2,3};
  int[] ch4 = {0,1,4};
  int[] ch5 = {0,1,4,5};
  int[] ch6 = {0,1,6};  


  color col_higlight = color(30,123,34,230);

  NetTopo(){
    // no con =D
  }
  
  void dsetup(){
  
  // this is fixed to 7 hardcoded channels
  // if more channels should be added this has be be redone
  channels[0] = ch0; 
  channels[1] = ch1;
  channels[2] = ch2;
  channels[3] = ch3;
  channels[4] = ch4; 
  channels[5] = ch5;
  channels[6] = ch6;

  colors[0]= color(#000000);    // black
  colors[1] = color(#0066DD);   // blue
  colors[2] = color(#00DDCC);   // tuerkis
  colors[3] = color(#77DD00);   // bluegreen
  colors[4] = color(#BBBBBB);   // grey
  colors[5] = color(#DD1100);   // red
  colors[6] = color(#DD00AA);   // pink 

  nodeNames[0] = "Demo Train";
  nodeNames[1] = "Deep Blue";
  nodeNames[2] = "Aquarius";
  nodeNames[3] = "Greenhorn";
  nodeNames[4] = "Safran";
  nodeNames[5] = "Red Cat";
  nodeNames[6] = "Mr. Pink";

  
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
  vecs[6] = new PVector(topoSizex*0.7,topoSizey*0.5);
  vecs[5] = new PVector(topoSizex*0.9,topoSizey*0.33);
  vecs[4] = new PVector(topoSizex*0.6,topoSizey*0.33);
  vecs[3] = new PVector(topoSizex*0.9,topoSizey*0.66);
  vecs[2] = new PVector(topoSizex*0.6,topoSizey*0.66);
  vecs[1] = new PVector(topoSizex*0.4,topoSizey*0.5);
  vecs[0] = new PVector(topoSizex*0.1,topoSizey*0.5);
  }
  
  void ddraw(int current_channel){
    noFill();
    strokeWeight(2);
    stroke(245,221,225,80);
    for (int[] ch : channels){
      beginShape();
      for(int c : ch){
        vertex(vecs[c].x, vecs[c].y);
      }
      endShape();
    }
    
    highlightChannel(current_channel%noKnots);

    int _ch = 0;
    for (PVector pv : vecs){
      pushMatrix();
        translate(pv.x-width/2,pv.y-height/2);

        drawNode(.1,.15,.1,.04,0.61,nodeRadius-1,nodeRadius,_ch);
        translate(width/2,height/2);
        
        // drawNodeText(_ch,current_channel);
        drawCircularNodeText(_ch,current_channel,nodeRadius);
        _ch++;
      popMatrix();
    }
 }
  
  void highlightChannel(int ch){
      strokeWeight(6);
      stroke(colors[ch]);
      noFill();
      beginShape();
        for(int c : channels[ch]){
          vertex(vecs[c].x, vecs[c].y);
        }
      endShape();

      noStroke();
      beginShape();
        for(int c : channels[ch]){
          ellipse(vecs[c].x, vecs[c].y,50,40);
        }
      endShape();

    
  }

// print text next to the knots
// i see the irony in int name as well, but dgaf
    void drawNodeText(int name, int current_channel){
    int xoff = 15;
    int yoff = -20;
    int xpitch = 0;
    int ypitch = 30;
    int _line = 0; // is there a convention to indicate counter vars??

    // underlying textbox
    //fill(0,150);
    noFill();
    // stroke(#BBBBBB);
    // strokeWeight(.2);
    noStroke();
    if(name==current_channel){
      stroke(col_higlight);
      strokeWeight(2);
    }
    // rect(xoff-3,yoff-20,nodeNames[name].length()*10,26);
    rect(xoff-3,yoff-20,textWidth(nodeNames[name])+10,26);

    fill(255,201);
    textSize(16);
    text(nodeNames[name],xoff, yoff + _line * ypitch);

    if(name==current_channel){
      _line++;
      fill(col_higlight);
      stroke(col_higlight);
      textSize(20);
      text("active",xoff, yoff-50 + _line * ypitch);
    }

    
  }

  void drawNode(float r_stepsize, float r_jitter, float t_stepsize, float strokew,float t_min, float rad_min, float rad_max, int colorId) { 
  pushMatrix();
  color b1 = color(255);
  color b2 = color(0);
  color c1 = color(204, 102, 0);
  color c2 = color(0, 102, 153);
  color r1 = color(random(255),random(255),random(255),random(255));

    translate(width/2., height/2.);
    float r_rand = random(r_jitter);
    PVector[] vs = generateRailLookUp(100);
    t_stepsize/=100000;
    
    //outer loop creates radial virtual lines
    for (float r=0; r<TWO_PI;r+= r_stepsize + r_rand) {
      r_rand = random(r_jitter); 
      
      int rr = int(map(r,0,TWO_PI,0,vs.length));
      println(rr);
      
      float rad_rand = random(rad_min,rad_max);
      float t_rand = random(0.001, t_stepsize);
      
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


void drawCircularNodeText(int name, int current_channel, float r) {
  //taken from processing page
  String message = nodeNames[name];
  float textOffset = 5;
  float textRadialOffset = 225;
  color col_ring = #CCCCCC;
  color col_text = #EEEEEE;
  PFont f = createFont("Georgia",15,true);
  


    textFont(f);
    // The text must be centered!
    textAlign(CENTER);


  // Start in the center and draw the circle
  //translate(width / 2, height / 2);
  noFill();
  stroke(col_ring);
  strokeWeight(2);
  if(name==current_channel||name==0){
    stroke(colors[current_channel]);
    strokeWeight(4);
  }
  ellipse(0, 0, r*2, r*2);

  // We must keep track of our position along the curve
  float arclength = 0;

  // For every box
  for (int i = 0; i < message.length(); i++)
  {
    // Instead of a constant width, we check the width of each character.
    char currentChar = message.charAt(i);
    float w = textWidth(currentChar);

    // Each box is centered so we move half the width
    arclength += w/2;
    // Angle in radians is the arclength divided by the radius
    // Starting on the left side of the circle by adding PI
    float theta = PI/180.*radialOffsets[name] + arclength / r;    

    pushMatrix();
    // Polar to cartesian coordinate conversion
    translate((r+textOffset)*cos(theta), (r+textOffset)*sin(theta));
    // Rotate the box
    rotate(theta+PI/2.); // rotation plus offset
    // Display the character
    fill(col_text);
    if(name==current_channel||name==0){
      fill(colors[current_channel]);
    }
    text(currentChar,0,0);
    popMatrix();
    // Move halfway again
    arclength += w/2;
  }
}
}
