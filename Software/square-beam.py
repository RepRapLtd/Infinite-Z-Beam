#
# FreeCAD Python Macro to make a beam printable on an infinite-Z printer.
#
# Adrian Bowyer
# reprapltd.com
#
# 4 August 2021
#
# Licence: GPL
#

#--------------------------------------------------------------------------------------------------------------

# Set the values you want in here. All dimensions are in mm.

# The overall size of the beam. Length must be the biggest dimension.
# Note the beam will be reoriented to make the Z direction the larger of 
# width and height, as that is the orientation in which it must be printed.

length = 200
width = 35
height = 25

# The thickness of the beam struts

thickness = 3

# The size of the mounting holes.
# Add 0.3 mm to the nominal size of the thread that will go through them.

holes = 3.3

#--------------------------------------------------------------------------------------------------------------

# Internal parameters. Change these to get interesting, but possibly incorrect, results.

angleFactor = 0.8
screwHoleCount = 12
screwGap = 5
screwPitch = 1.5

import Part, FreeCAD, math
from FreeCAD import Base
import math as maths
import random

# There must be an easier way to make a null set...
# See: https://forum.freecadweb.org/viewtopic.php?f=22&t=35237&p=522227#p522227

def NullSet():
 a = Part.makeBox(1, 1, 1)
 a.translate(Base.Vector(10, 10, 10))
 return a.common(Part.makeBox(1, 1, 1))

# Create a diagonal of thickness t on a face (0 ... 5) of cuboid (x, y, z).

def Diagonal(x, y, z, t, face):
 if face == 0:
  d = maths.sqrt(x*x + y*y)*2
  b = Part.makeBox(d, t, t)
  b.translate(Base.Vector(0, -0.5*t, 0))
  angle = maths.atan2(y, x)
  b.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), angle*180/maths.pi)
  return b
 elif face == 1:
  d = maths.sqrt(x*x + y*y)*2
  b = Part.makeBox(d, t, t)
  b.translate(Base.Vector(0, y - 0.5*t, z - t))
  angle = -maths.atan2(y, x)
  b.rotate(Base.Vector(0, y, 0), Base.Vector(0, 0, 1), angle*180/maths.pi)
  return b
 elif face == 2:
  d = maths.sqrt(x*x + z*z)*2
  b = Part.makeBox(d, t, t)
  b.translate(Base.Vector(0, 0, -0.5*t))
  angle = -maths.atan2(z, x)
  b.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 1, 0), angle*180/maths.pi)
  return b
 elif face == 3:
  d = maths.sqrt(x*x + z*z)*2
  b = Part.makeBox(d, t, t)
  b.translate(Base.Vector(0, y - t, z - 0.5*t))
  angle = maths.atan2(z, x)
  b.rotate(Base.Vector(0, 0, z), Base.Vector(0, 1, 0), angle*180/maths.pi)
  return b
 elif face == 4:
  d = maths.sqrt(y*y + z*z)*2
  b = Part.makeBox(t, d, t)
  b.translate(Base.Vector(0, 0, -0.5*t))
  angle = maths.atan2(z, y)
  b.rotate(Base.Vector(0, 0, 0), Base.Vector(1, 0, 0), angle*180/maths.pi)
  return b
 elif face == 5:
  d = maths.sqrt(y*y + z*z)*2
  b = Part.makeBox(t, d, t)
  b.translate(Base.Vector(x - t, 0, z - 0.5*t))
  angle = -maths.atan2(z, y)
  b.rotate(Base.Vector(0, 0, z), Base.Vector(1, 0, 0), angle*180/maths.pi)
  return b
 print("Diagonal(x, y, z, t, face) - face must be in [0, 5]")

# Create a single beam box. If diagonals is False, just the cuboid is created.
# If it's true the cuboid is decomposed into tetrahedra. If bothEnds is False the
# +x end rectangle is omitted. If endDiagonals is false, the -x and +x diagonals are omitted.

def OutlineBox(x, y, z, t, diagonals, bothEnds, endDiagonals):
 xb = Part.makeBox(x + 2, y - 2*t, z - 2*t)
 xb.translate(Base.Vector(-1, t, t))
 if bothEnds:
  xAdd = -2*t
 else:
  xAdd = 2*t
 yb = Part.makeBox(x + xAdd, y + 2 , z - 2*t)
 yb.translate(Base.Vector(t, -1, t))
 zb = Part.makeBox(x + xAdd, y - 2*t, z + 2)
 zb.translate(Base.Vector(t, t, -1))
 u = xb.fuse(yb)
 u = u.fuse(zb)
 v = Part.makeBox(x, y, z)
 u = v.cut(u)
 if not diagonals:
  return u
 u = u.fuse(Diagonal(x, y, z, t, 0).common(v))
 u = u.fuse(Diagonal(x, y, z, t, 1).common(v))
 u = u.fuse(Diagonal(x, y, z, t, 2).common(v))
 u = u.fuse(Diagonal(x, y, z, t, 3).common(v))
 if endDiagonals:
  u = u.fuse(Diagonal(x, y, z, t, 4).common(v))
  u = u.fuse(Diagonal(x, y, z, t, 5).common(v))
 return u

# Create a ring of screw holes with their axes in the z direction. Note the small
# random purturbations on the radii. Without this the ScrewHoles() function
# below can't form the union of all the cylinders as there are too many tangential
# coincidences. This is very nasty, but, hey, B-Rep modellers...
# The pitch circle is rounded to the nearest 0.5mm.

def ZScrewHolePattern(y, z, t, d):
 sh = NullSet()
 h = y - screwGap*d
 pitchRadius = 0.5*round(2.0*(h/2 + screwPitch*d + y/2))
 trans = Base.Vector(pitchRadius, y/2, -0.1)
 centre = Base.Vector(y/2, y/2, 0)
 axis = Base.Vector(0, 0, 1)
 for s in range(screwHoleCount):
  cyl = Part.makeCylinder(d/2 + random.uniform(-0.01, 0.01), z + 0.2)
  cyl.translate(trans)
  cyl.rotate(centre, axis, s*360/screwHoleCount)
  sh = sh.fuse(cyl)
 return (sh, pitchRadius)

# Make three orthogonal screw hole patterns to allow the beams to be attached to
# themselves or other things. Tell the user what they need to know.

def ScrewHoles(y, z, t, d):
 zhp2 = ZScrewHolePattern(y, z, t, d)
 zhp = zhp2[0]
 print("There are " + str(screwHoleCount) + " screw holes for attachment with diameter " + str(d) + " mm on a pitch circle of " + str(zhp2[1]) + " mm.")
 sh = NullSet()
 sh = sh.fuse(zhp)
 zhp = ZScrewHolePattern(y, y, t, d)[0]
 zhp.translate(Base.Vector(0, 0, (z - y)/2))
 centre = Base.Vector(y/2, y/2, z/2)
 zhp.rotate(centre, Base.Vector(1, 0, 0), 90)
 sh = sh.fuse(zhp)
 zhp.rotate(centre, Base.Vector(0, 0, 1), 90)
 sh = sh.fuse(zhp)
 return sh

# The central holes in the ends of the beams to allow wires to be run along them and so on.

def CentalHoles(y, z, d):
 ch = NullSet()
 h = y - screwGap*d
 cyl = Part.makeCylinder(h/2, z + 2)
 cyl.translate(Base.Vector(y/2, y/2, -1))
 ch = ch.fuse(cyl)
 centre = Base.Vector(y/2, y/2, z/2)
 cyl.rotate(centre, Base.Vector(1, 0, 0), -90)
 ch = ch.fuse(cyl)
 cyl.rotate(centre, Base.Vector(0, 0, 1), 90)
 ch = ch.fuse(cyl)
 return ch

# The solid ends.

def EndBlock(x, y, z):
 b = Part.makeBox(x, y, z)
 return b

# Build the entire beam

def Beam(x, y, z, t, d):
 y1 = min(y, z)
 z = max(y, z)
 y = y1
 step = angleFactor*y
 len = x + t - 2*y
 steps = int(len/(step - t)) + 1
 step = len/steps
 xi = y - t
 beam = NullSet()
 d1 = True
 for s in range(steps):
  ob = OutlineBox(step + t, y, z, t, True, False, d1)
  d1 = not d1
  ob.translate(Base.Vector(xi, 0, 0))
  beam = beam.fuse(ob)
  xi += step
 eb = EndBlock(y, y, z)
 beam = beam.fuse(eb)
 otherEnd = Base.Vector(len + y - t, 0, 0)
 eb.translate(otherEnd)
 beam = beam.fuse(eb)
 sh = ScrewHoles(y, z, t, d)
 beam = beam.cut(sh)
 sh.translate(otherEnd)
 beam = beam.cut(sh)
 ch = CentalHoles(y, z, d)
 beam = beam.cut(ch)
 ch.translate(otherEnd)
 beam = beam.cut(ch)
 return beam

beam = Beam(length, width, height, thickness, holes)
Part.show(beam)
