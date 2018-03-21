
// No license, but send me a hello if you use this for some good purpose.
// -- Mirek Kratochvil <exa.exa@gmail.com>

//TODO: round corners?

font = "Consolas"; //URW Bookman L looks nicely here as well
font2 = "Droid Sans Mono";

alphabet = "en";

//inch-sized tiles look imperial.
tilesize=25.4;
//you might like them a bit larger if you want to use this outdoors

//distance between tiles
off=tilesize*1.1;
//height 1/8"
tileheight=tilesize/8;
fontheight=tileheight*0.5;

//accomodate for Ё
if (alphabet=="ru") { 
        fontheight=fontheight*0.9;
}

//this produces one tile
module tilec(letter, x, y, c) {
  translate([x*off,(6-y)*off,0]) {
    difference() {
      color(c)
      cube([tilesize,tilesize,tileheight]);
      color(c)
        translate([tilesize*.4,tilesize*.4,tileheight*.51])
        linear_extrude (height=tileheight/2)
          text(letter, font=font, size=tilesize*.45,
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

module tiles(letters) {
    for(i=[0,1,2,3,4,5,6]) for (j=[0,1,2,3,4,5,6]) {
        tile(letters[i+7*j], i, j);
    }
}

if (alphabet=="en") {
    // latin variant of tiles
    tiles(
        ["_", "A", "B", "C", "D", "E", "F",
        "G", "H", "I", "J", "K", "L", "M",
        "N", "O", "P", "Q", "R", "S", "T",
        "U", "V", "W", "X", "Y", "Z", ".",
        "0", "1", "2", "3", "4", "5", "6",
        "7", "8", "9", ",", "-", "+", "*",
        "/", ":", "?", "!", "'", "(", ")"]
    );
} else if (alphabet=="ru") {
    // variant of tiles thanks to Stas Bushuev
    // (see https://github.com/Xitsa/ls47 for other versions)
    tiles(
        ["_", "А", "Б", "В", "Г", "Д", "Е",
        "Ё", "Ж", "З", "И", "Й", "К", "Л",
        "М", "Н", "О", "П", "Р", "С", "Т",
        "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ",
        "Ъ", "Ы", "Ь", "Э", "Ю", "Я", "/",
        "0", "1", "2", "3", "4", "5", "6",
        "7", "8", "9", ".", ",", "?", "!"]
    );
}

//the token
translate([-off/2,off/2,0]) {
    color("red") difference() {
      cylinder(h=tileheight, d=tilesize*.7);
      translate([0,0,-.1])
        cylinder(h=tileheight*1.2, d=tilesize*.7-tileheight);
    }
}


