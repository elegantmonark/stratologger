// Parametric two-piece PETG enclosure for the telemetry payload.
// Author: Trishan Biswas
// Project started: February 2026
// Status: Ongoing
// Measure your exact boards and edit the parameter block before final printing.
// Select: "base", "lid", or "print_both".
part = "print_both";

$fn = 48;

// Overall envelope.
case_x = 132;
case_y = 92;
base_z = 27;
lid_z = 3;
wall = 2.4;
floor_t = 2.4;
corner_r = 6;
clearance = 0.30;       // Per side for the lid locating lip.

// Nominal SL-1 PCB and mounting geometry.
pcb_x = 90;
pcb_y = 70;
pcb_origin = [8, 11];
pcb_hole_inset = 4.5;
standoff_od = 8;
standoff_hole = 3.2;    // M3 clearance; tune for printer.
standoff_h = 5;

// Lid interfaces; dimensions are intentionally easy to calibrate.
display_window = [50.5, 38.5];
display_center = [case_x/2, case_y/2];
tft_hole_spacing = [58, 45];
tft_screw_hole = 2.4;
button_center = [108, 58];
button_hole_d = 7.2;

// Side openings in the base.
usb_cutout_width = 14;
usb_cutout_height = 9;
usb_cutout_x = 25;      // Along the front (y=0) wall.
power_switch_width = 13;
power_switch_height = 8;
power_switch_x = 103;

module rounded_prism(size, radius) {
    hull() {
        for (x = [radius, size[0] - radius])
            for (y = [radius, size[1] - radius])
                translate([x, y, 0]) cylinder(r=radius, h=size[2]);
    }
}

module hollow_base() {
    difference() {
        rounded_prism([case_x, case_y, base_z], corner_r);
        translate([wall, wall, floor_t])
            rounded_prism([case_x - 2*wall, case_y - 2*wall,
                           base_z - floor_t + 1],
                          max(1, corner_r - wall));

        // Front-wall USB and power-switch openings.
        translate([usb_cutout_x - usb_cutout_width/2, -1,
                   floor_t + standoff_h + 1])
            cube([usb_cutout_width, wall + 2, usb_cutout_height]);
        translate([power_switch_x - power_switch_width/2, -1,
                   floor_t + 5])
            cube([power_switch_width, wall + 2, power_switch_height]);

        // Two low ventilation banks beside, not beneath, the environmental sensor.
        for (z = [8:4:20])
            translate([-1, 19, z])
                rotate([0, 90, 0]) cylinder(d=2.2, h=wall + 2);
        for (z = [8:4:20])
            translate([-1, 27, z])
                rotate([0, 90, 0]) cylinder(d=2.2, h=wall + 2);
    }
}

module screw_standoff(position) {
    translate([position[0], position[1], floor_t])
        difference() {
            cylinder(d=standoff_od, h=standoff_h);
            translate([0, 0, -0.1])
                cylinder(d=standoff_hole, h=standoff_h + 0.2);
        }
}

module base() {
    union() {
        hollow_base();

        // SL-1 PCB mounting points.
        for (x = [pcb_origin[0] + pcb_hole_inset,
                  pcb_origin[0] + pcb_x - pcb_hole_inset])
            for (y = [pcb_origin[1] + pcb_hole_inset,
                      pcb_origin[1] + pcb_y - pcb_hole_inset])
                screw_standoff([x, y]);

        // Simple end stops for a removable 18650 holder in the right-side bay.
        translate([111, 9, floor_t]) cube([18, 3, 5]);
        translate([111, 80, floor_t]) cube([18, 3, 5]);
    }
}

module lid_plate() {
    difference() {
        rounded_prism([case_x, case_y, lid_z], corner_r);

        // Active display aperture in landscape orientation.
        translate([display_center[0] - display_window[0]/2,
                   display_center[1] - display_window[1]/2, -1])
            cube([display_window[0], display_window[1], lid_z + 2]);

        // TFT mounting holes, based on measured module hole spacing.
        for (x = [-tft_hole_spacing[0]/2, tft_hole_spacing[0]/2])
            for (y = [-tft_hole_spacing[1]/2, tft_hole_spacing[1]/2])
                translate([display_center[0] + x,
                           display_center[1] + y, -1])
                    cylinder(d=tft_screw_hole, h=lid_z + 2);

        translate([button_center[0], button_center[1], -1])
            cylinder(d=button_hole_d, h=lid_z + 2);

    }
}

module locating_lip() {
    lip_outer_x = case_x - 2*wall - 2*clearance;
    lip_outer_y = case_y - 2*wall - 2*clearance;
    lip_t = 1.5;
    translate([wall + clearance, wall + clearance, -3])
        difference() {
            rounded_prism([lip_outer_x, lip_outer_y, 3],
                          max(1, corner_r - wall));
            translate([lip_t, lip_t, -0.1])
                rounded_prism([lip_outer_x - 2*lip_t,
                               lip_outer_y - 2*lip_t, 3.2],
                              max(1, corner_r - wall - lip_t));
        }
}

module lid() {
    union() {
        lid_plate();
        locating_lip();
    }
}

if (part == "base") {
    base();
} else if (part == "lid") {
    lid();
} else {
    base();
    // Lid is placed flat beside the base for STL export/slicing.
    translate([case_x + 12, 0, 3]) rotate([180, 0, 0]) lid();
}

