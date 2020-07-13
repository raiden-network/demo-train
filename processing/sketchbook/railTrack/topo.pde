/////////////////////////////////////////////
//this class generates the inner topologie//
///////////////////////////////////////////
class NetTopo{

  // global vars
     
    //             4 - 5
    //            /
    //       0 - 1 - 6
    //            \
    //             2 - 3   

   

    int noKnots = 7;                          // if you want to add more redo this!!
    float nodeRadius = 30;                    // size of the circles

    int topoSizex = int(900*2/3.);            // overall size of the topologie
    int topoSizey = int(900*2/3.);
    
    color[] colors = new color[noKnots];      // oo was yesterday
    String[] nodeNames = new String[noKnots]; // arrays are back
    PVector[] vecs = new PVector[noKnots];
     
    float[] radialOffsets = {                 // angular offsets for the curved text
                              180,            // CW from 3 o'clock in degrees
                              180,
                              225,
                              225,
                              225,
                              225,
                              225
                            };


    int[][] channels = new int [noKnots][6];  // connections or statechannels
    int[] ch0 = {0};
    int[] ch1 = {0,1,1};
    int[] ch2 = {0,1,2};
    int[] ch3 = {0,1,2,3};
    int[] ch4 = {0,1,4};
    int[] ch5 = {0,1,4,5};
    int[] ch6 = {0,1,6};  

    color col_higlight = color(30,123,34,130);  // only used in drawNodeText <- deprecated

  NetTopo(){
    // no con =D
  }
  
  // init all the arrays
  void dsetup(){
    
    // this is fixed to 7 hardcoded channels
    // if (a lot) more channels should be added this has be be redone
    channels[0] = ch0; 
    channels[1] = ch1;
    channels[2] = ch2;
    channels[3] = ch3;
    channels[4] = ch4; 
    channels[5] = ch5;
    channels[6] = ch6;

    // careful! colors also in landscape
    colors[0]= color(#000000);    // black
    colors[1] = color(#0066DD);   // blue
    colors[2] = color(#00DDCC);   // tuerkis
    colors[3] = color(#77DD00);   // bluegreen
    colors[4] = color(#FFFF00);   // yellow
    colors[5] = color(#DD1100);   // red
    colors[6] = color(#DD00AA);   // pink 

    nodeNames[0] = "Train";
    nodeNames[1] = "Blue inc";
    nodeNames[2] = "Aquarius AG";
    nodeNames[3] = "Green Ltd";
    nodeNames[4] = "Yellow Group";
    nodeNames[5] = "Red Systems";
    nodeNames[6] = "Pink Industries";

    
     // the position of the nodes is also hardcoded below
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


    //horizontal positioning
    vecs[6] = new PVector(topoSizex*0.7,topoSizey*0.5);
    vecs[5] = new PVector(topoSizex*0.9,topoSizey*0.33);
    vecs[4] = new PVector(topoSizex*0.6,topoSizey*0.33);
    vecs[3] = new PVector(topoSizex*0.9,topoSizey*0.66);
    vecs[2] = new PVector(topoSizex*0.6,topoSizey*0.66);
    vecs[1] = new PVector(topoSizex*0.4,topoSizey*0.5);
    vecs[0] = new PVector(topoSizex*0.1,topoSizey*0.5);

  }
  
  // main draw function for this class
  void ddraw(int current_channel){
    
    noFill();                                   // draw params for normal connection lines
    strokeWeight(2);
    stroke(245,221,225,80);
    
    for (int[] ch : channels){                  // draw normal connection lines
      beginShape();
        for(int c : ch){
          vertex(vecs[c].x, vecs[c].y);
        }
      endShape();
    }
    
    highlightChannel(current_channel%noKnots);  // draw active connection line

    int _ch = 0;
    for (PVector pv : vecs){                    // iterate over all nodes
      pushMatrix();
        translate(pv.x-width/2,pv.y-height/2);

        drawNode(.1,.15,.1,.04,0.61,nodeRadius-1,nodeRadius,_ch); // actually draw the node
        translate(width/2,height/2);
        
        // drawNodeText(_ch,current_channel);                     // uncomment to draw straight text
        drawCircularNodeText(_ch,current_channel,nodeRadius);     // draw the curved text
        _ch++;
      popMatrix();
    }
 }
  
  // draw active connection line with special color
  void highlightChannel(int ch){
      strokeWeight(6);                  // draw-params for highlight line 
      stroke(colors[ch]);
      noFill();

      beginShape();                     // draw the line
        for(int c : channels[ch]){
          vertex(vecs[c].x, vecs[c].y);
        }
      endShape();

      noStroke();                       // draw-params for circles on line
      fill(colors[ch]);                 // all circles color of active node

      beginShape();                     // draw circles
        for(int c : channels[ch]){
          // fill(colors[c]);           // circles in own colors
          ellipse(vecs[c].x, vecs[c].y,20,20);
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

  // this draws the color gradient in the nodes, similar to the landscape generator
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

  // draw the curved text around the nodes
  void drawCircularNodeText(int name, int current_channel, float r) {
    //this is mostly taken from processing page
    String message = nodeNames[name];
    float textOffset = 5;
    float textRadialOffset = 225;
    color col_ring = #CCCCCC;
    color col_text = #EEEEEE;
    PFont f = createFont("Roboto",15,true);
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
