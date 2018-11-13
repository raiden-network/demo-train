class NetTopo{
  Wiggler j = new Wiggler();
  int noKnots = 7;
  PVector[] items = new PVector[noKnots];
  Wiggler[] wiggls = new Wiggler[noKnots];
   int topoSizex = 600;
   int topoSizey = 600;
  int blobSize = topoSizex/12;
  int[][] channels = new int [noKnots][6];
  int[] ch0 = {0};
  int[] ch1 = {0,1};
  int[] ch2 = {0,1,2};
  int[] ch3 = {0,1,2,3};
  int[] ch4 = {0,1,4};
  int[] ch5 = {0,1,4,5};
  int[] ch6 = {0,1,6};
  
  
  void setup(){
   size(600,600,P2D);
   background(0);
  
   channels[0] = ch0; 
   channels[1] = ch1;
   channels[2] = ch2;
   channels[3] = ch3;
   channels[4] = ch4; 
   channels[5] = ch5;
   channels[6] = ch6;
  
   items[6] = new PVector(topoSizex/5,topoSizey*2/7);
   items[5] = new PVector(topoSizex/4,topoSizey*41/55);
   items[4] = new PVector(topoSizex/3,topoSizey/2.);
   items[3] = new PVector(topoSizex*22./33.,topoSizey*25./34.);
   items[2] = new PVector(topoSizex*2./3.,topoSizey/2.);
   items[1] = new PVector(topoSizex/2.,topoSizey*35./90.);
   items[0] = new PVector(topoSizex/2.,topoSizey/7.);
   
   for(int i = 0; i < items.length; i++){
     wiggls[i] = new Wiggler(int(items[i].x), int(items[i].y),blobSize,str(i));
   }
  }
  
  void draw(){
    background(0);
    
    noFill();
    strokeWeight(2);
    stroke(230,223,254,70);
    for (int[] ch : channels){
      beginShape();
      for(int c : ch){
        vertex(items[c].x, items[c].y);
        wiggls[c].setColor(color(200,0,0,40));
      }
      endShape();
    }
   
  highlightChannel(second()%noKnots);
  
  
    for (Wiggler w : wiggls){
       w.display();
       w.wiggle();
       w.texto();
    }
    
      
  
  }
  
  void highlightChannel(int ch){
      noFill();
      strokeWeight(7);
      stroke(30,223,54,60);
      beginShape();
        for(int c : channels[ch]){
          vertex(items[c].x, items[c].y);
          wiggls[c].setColor(color(6,250,10,40));
        }
      endShape();
    
  }
  
  void drawKnot(int x, int y, String name){
    fill(236,37,167);
    stroke(12,34,56);
    ellipse(x,y,100,100);
    //textMode(CENTER);
    text(name,x+150,y);
  }
}

// An object that wraps the PShape
