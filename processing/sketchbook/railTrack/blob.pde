// An object that wraps the PShape

class Wiggler {
  
  // The PShape to be "wiggled"
  PShape s;
  // Its location
  float x, y;
  
  String name;
  
  // For 2D Perlin noise
  float yoff = 0;
  
  // We are using an ArrayList to keep a duplicate copy
  // of vertices original locations.
  ArrayList<PVector> original;
  
  color col = color(245,234,189,145);

  Wiggler(int xx, int yy, int mult, String n) {
    x = xx;
    y = yy; 
    name = n;

    // The "original" locations of the vertices make up a circle
    original = new ArrayList<PVector>();
    for (float a = 0; a < TWO_PI; a+=0.2) {
      PVector v = PVector.fromAngle(a);
      v.mult(mult);
      original.add(v);
    }
    
    // Now make the PShape with those vertices
    s = createShape();
    s.beginShape();
    s.fill(col);
    //s.stroke(255,70);
    s.strokeWeight(1);
    for (PVector v : original) {
      s.vertex(v.x, v.y);
    }
    s.endShape(CLOSE);
  }

  void wiggle() {
    
    float xoff = 0;
    // Apply an offset to each vertex
    for (int i = 0; i < s.getVertexCount(); i++) {
      // Calculate a new vertex location based on noise around "original" location
      PVector pos = original.get(i);
      float a = TWO_PI*noise(xoff,yoff);
      PVector r = PVector.fromAngle(a);
      r.mult(1.5);
      r.add(pos);
      // Set the location of each vertex to the new one
      s.setVertex(i, r.x, r.y);
      // increment perlin noise x value
      xoff+= 0.5;
    }
    // Increment perlin noise y value
    yoff += 0.02;
  }

  void display() {
    pushMatrix();
    translate(x+random(2), y+random(2));
    shape(s);
    popMatrix();
  }
  
  void texto(){
    fill(255,10);
    textSize(90);
    //textMode(CENTER);
    text(name,x+14,y+23);
    fill(255,30);
    textSize(95);
    //textMode(CENTER);
    text("R"+name,x-14,y+27);
        fill(255,65);
    textSize(55);
    //textMode(CENTER);
    text(name,x+34,y+23);
}
    
  void setColor(color c){  
    s.setFill(c);
  }
}
