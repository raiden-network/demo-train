void setup(){
 fullScreen(P3D);
 background(0);
}

void draw(){
  PImage img = loadImage("../../current_barcode.jpg");
  beginShape();
  texture(img);

  vertex(0, 0, 0, 0);
  vertex(100, 0, 400, 0);
  vertex(100, 100, 400, 400);
  vertex(0, 100, 0, 400);
  endShape();
}
