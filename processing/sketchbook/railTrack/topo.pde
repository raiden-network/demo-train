/////////////////////////////////////////////
//this class generates the inner topologie//
///////////////////////////////////////////
class NetTopo{

  color[] colors = new color[8];
  int noKnots = 7;
  PVector[] vecs = new PVector[noKnots];
  // Wiggler[] wiggls = new Wiggler[noKnots];
  //TunnelLandscape[] tunnels = new TunnelLandscape[noKnots];
  int topoSizex = int(900*2/3.);
  int topoSizey = int(900*2/3.);
  int blobSize = topoSizex/18;
  int[][] channels = new int [noKnots][6];
  int[] ch0 = {0};
  int[] ch1 = {0,1,0};
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

  colors[0]= color(#BBBBBB); 
  colors[1] = color(#0066DD); 
  colors[2] = color(#00DDCC); 
  colors[3] = color(#BBDD00); 
  colors[4] = color(#DDBB00); 
  colors[5] = color(#DD1100); 
  colors[6] = color(#DD00AA); 
  colors[7] = color(#DD00AA); 
  
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


  //  for(int i = 0; i < vecs.length; i++){
  //    wiggls[i] = new Wiggler(int(vecs[i].x), int(vecs[i].y),blobSize,str(i));
  //  }
  }
  
  void ddraw(int current_channel){
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

        drawNode(.1,.15,.1,.04,0.48,45.,48.,_ch);
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
  
  void highlightChannel(int ch){
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
    void texto(int name, int current_channel){
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
}
