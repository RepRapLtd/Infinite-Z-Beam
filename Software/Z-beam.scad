// parametric beam with cable-running spaces
// ported to OpenSCAD from the Python code, with variable descriptions modified
// to be customizer-compatible
// see https://reprapltd.com/3d-printed-beam-that-is-as-stiff-as-steel/

// ---------------------------------------------------------------------------

// Set the values you want in here. All dimensions are in mm.

// The overall size of the beam. Length must be the biggest dimension.
// Note the beam will be reoriented to make the Z direction the larger of 
// width and height, as that is the orientation in which it must be printed.

// beam length; must be the biggest dimension
length = 200;
// width of the beam
width = 35;
// height of the beam
height = 25;

// The thickness of the beam struts
thickness = 3;

// The size of the mounting holes.
holeSize = 3;

// Number of mounting holes at each end 
screwHoleCount = 12;

// Style of diagonal struts
diagStyle = "tetra"; // ["tetra", "octa", "Z"]

// ---------------------------------------------------------------------------

// Internal parameters. Change these to get interesting, but possibly
// incorrect, results.

// [internal] box height as ratio of shortest dimension
angleFactor = 0.8;
// [internal] gap between screw holes
screwGap = 5;
// [internal] additional relative adjustment for screw spacing
screwPitch = 1.5;
// [internal] small adjustment to remove intersecting vertices
sigma = 0.01;
// [internal] additional size for hole cuts
holeDelta = 0.3;

// Create the beam

x = length;
y = min(height, width);
z = max(height, width);
boxStep1 = angleFactor * y;
boxLen = x + thickness - 2*y;
numSteps = floor(boxLen / (boxStep1 - thickness)) + 1;
boxStep = boxLen / numSteps;
xi = y - thickness;

// outline box
module OutlineBox(endForm = 3, flipDiags = false){
    if(endForm > 0){
      // top / bottom
      xtrans = 
        (endForm == 1) ? [0]:
        (endForm == 2) ? [boxStep]:
        (endForm == 3) ? [0, boxStep]: [];
      for(xtran = xtrans){
          translate([0,0,xtran]) linear_extrude(thickness) difference(){
              square([y,z]);
              offset(-thickness) square([y,z]);
          }
      }
    }
    // corner struts
    ssz = thickness / 2;
    strutStarts = [[0, 0,           ssz], [y-thickness, 0,           ssz],
                   [0, z-thickness, ssz], [y-thickness, z-thickness, ssz]];
    for(strutStart = strutStarts){
        translate(strutStart) cube([thickness, thickness, boxStep]);
    }
    // diagonals
    yol = y - 2 * thickness;
    zol = z - 2 * thickness;
    xol = boxStep - thickness;
    dlx = sqrt(yol*yol + zol*zol) + sigma;
    dly = sqrt(yol*yol + xol*xol) + sigma;
    dlz = sqrt(zol*zol + xol*xol) + sigma;
    diagMul1 = 
       (diagStyle == "Z") ?     [-1,  1, -1,  1,  1,  1] :
       (diagStyle == "tetra") ? [ 1, -1, -1,  1, -1, -1] :
       (diagStyle == "octa") ?  [ 1, -1, -1,  1, -1, -1] :
           [1, 1, 1, 1, 1, 1];
    diagMul = (flipDiags) ? diagMul1 * -1 : diagMul1;
    // left
    translate([y/2,0,(boxStep+thickness)/2])
        rotate([0,diagMul[0] * atan2(xol, yol)+90,0])
          translate([-thickness/2,0,-dly/2])
            cube([thickness, thickness, dly]);
    // right
    translate([y/2,z-thickness,(boxStep+thickness)/2])
        rotate([0,diagMul[1] * atan2(xol, yol)+90,0])
          translate([-thickness/2,0,-dly/2])
            cube([thickness, thickness, dly]);
    // front
    translate([0,z/2,(boxStep+thickness)/2])
        rotate([diagMul[2] * atan2(xol, zol)+90,0,0])
          translate([0,-thickness/2,-dlz/2])
            cube([thickness, thickness, dlz]);
    // back
    translate([y-thickness,z/2,(boxStep+thickness)/2])
        rotate([diagMul[3] * atan2(xol, zol)+90,0,0])
          translate([0,-thickness/2,-dlz/2])
            cube([thickness, thickness, dlz]);
    // internal bottom
    if((endForm == 1) || (endForm == 3)){
      translate([y/2, z/2, thickness/2])
        rotate(diagMul[4] * atan2(zol, yol)+90) rotate([90,0,0])
          translate([-thickness/2,-thickness/2,-dlx/2])
            cube([thickness, thickness, dlx]);
    }
    // internal top [not usually printed]
    if((endForm == 2) || (endForm == 3)){
      translate([y/2, z/2, boxStep + thickness/2])
        rotate(diagMul[5] * atan2(zol, yol)+90) rotate([90,0,0])
          translate([-thickness/2,-thickness/2,-dlx/2])
            cube([thickness, thickness, dlx]);
    }
}

module EndBlock(report=false){
  holeSizeAdj = holeSize + holeDelta;
  largeDiam = y - screwGap * (holeSizeAdj);
  pitchRadius = 0.5*round(2.0*(largeDiam/2 + 
                  screwPitch*(holeSizeAdj)));
  difference(){
    cube([y,z,y]);
    // large hole cuts
    translate([y/2,z/2,y/2]) {
      rotate([90,0,0]) cylinder(h=z*2, d=largeDiam, center=true, $fn=61);
      rotate([0,90,0]) cylinder(h=z*2, d=largeDiam, center=true, $fn=61);
      rotate([0,0, 0]) cylinder(h=z*2, d=largeDiam, center=true, $fn=61);
    }
    // screw hole cuts
    translate([y/2,z/2,y/2]) {
      rotate([90,0,0]) for(rti = [0:(screwHoleCount-1)]){
        rotate(rti * (360 / screwHoleCount)) translate([pitchRadius,0,0]){
          cylinder(d=holeSizeAdj, h=z*2, center=true, $fn=13);
        }
      }
      rotate([0,90,0]) for(rti = [0:(screwHoleCount-1)]){
        rotate(rti * (360 / screwHoleCount)) translate([pitchRadius,0,0]){
          cylinder(d=holeSizeAdj, h=z*2, center=true, $fn=13);
        }
      }
      for(rti = [0:(screwHoleCount-1)]){
        rotate(rti * (360 / screwHoleCount)) translate([pitchRadius,0,0]){
          cylinder(d=holeSizeAdj, h=z*2, center=true, $fn=13);
        }
      }
    }
  }
  // Tell the user what they need to know.
  if(report){
    echo(str("There are ", screwHoleCount, " screw holes for attachment with diameter ",
         holeSize," mm on a pitch circle of ", pitchRadius, " mm."));
  }
}

// bottom end block
EndBlock(report=true);

// struts
for(xi = [0 : numSteps-1]){
  translate([0,0,xi*boxStep-thickness+y])
    OutlineBox(endForm = ((xi == 0) ? 0 : 1),
               flipDiags = ((diagStyle=="octa") && (xi % 2 == 0)));
}

// top end block
translate([0,0,length-y]) EndBlock();