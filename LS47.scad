// text_on_cube.scad - Example for text() usage in OpenSCAD

echo(version=version());

//font = "URW Bookman L";
font = "Monospace";
font2 = "Droid Sans Mono";
//TODO: kulaty rohy

tilesize=25.4;

off=tilesize*1.05;
tileheight=tilesize/8;

module tilec(letter, x, y, c) {
  translate([x*off,(6-y)*off,0]) {
    difference() {
      color(c)
      cube([tilesize,tilesize,tileheight]);
      color(c)
        translate([tilesize*.4,tilesize*.4,tileheight*.51])
        linear_extrude (height=tileheight/2)
          text(letter, font=font, size=tilesize*.5,
               halign="center", valign="baseline");
      color(c)
      translate([tilesize*.83, tilesize/2, tileheight*.76])
        linear_extrude(height=tileheight/4)
          text(str(x), font=font2, size=tilesize*.2,
               halign="center", valign="center");
      color(c)
      translate([tilesize/2, tilesize*.14, tileheight*.76])
        linear_extrude(height=tileheight/4)
          text(str(y), font=font2, size=tilesize*.2,
               halign="center", valign="center");
    }
  }
}

//tiles

module tile(letter,x,y) {
   tilec(letter,x,y,"darkgray");
}

tile("_",0,0);
tile("A",1,0);
tile("B",2,0);
tile("C",3,0);
tile("D",4,0);
tile("E",5,0);
tile("F",6,0);
tile("G",0,1);
tile("H",1,1);
tile("I",2,1);
tile("J",3,1);
tile("K",4,1);
tile("L",5,1);
tile("M",6,1);
tile("N",0,2);
tile("O",1,2);
tile("P",2,2);
tile("Q",3,2);
tile("R",4,2);
tile("S",5,2);
tile("T",6,2);
tile("U",0,3);
tile("V",1,3);
tile("W",2,3);
tile("X",3,3);
tile("Y",4,3);
tile("Z",5,3);
tile(".",6,3);
tile("0",0,4);
tile("1",1,4);
tile("2",2,4);
tile("3",3,4);
tile("4",4,4);
tile("5",5,4);
tile("6",6,4);
tile("7",0,5);
tile("8",1,5);
tile("9",2,5);
tile(",",3,5);
tile("-",4,5);
tile("+",5,5);
tile("*",6,5);
tile("/",0,6);
tile(":",1,6);
tile("?",2,6);
tile("!",3,6);
tile("'",4,6);
tile("(",5,6);
tile(")",6,6);


//the token
translate([-off/2,off/2,0]) {
    color("red") difference() {
      cylinder(h=tileheight, d=tilesize*.7);
      translate([0,0,-.1])
        cylinder(h=tileheight*1.2, d=tilesize*.7-tileheight);
    }
}
