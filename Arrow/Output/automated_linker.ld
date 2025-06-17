MEMORY
{
  trickbox_mem : ORIGIN = 0x13000000, LENGTH = 0x200000
  memory_region_utilities : ORIGIN = 0x80000000, LENGTH = 0x200000000
  memory_region_core_0_el3_root : ORIGIN = 0x80200000, LENGTH = 0x280200000
  memory_region_core_0_el1_ns : ORIGIN = 0x80200000, LENGTH = 0x280200000
  memory_region_core_1_el3_root : ORIGIN = 0x80200000, LENGTH = 0x280200000
  memory_region_core_1_el1_ns : ORIGIN = 0x80200000, LENGTH = 0x280200000
}

SECTIONS
{
  .data.trickbox 0x13000000 :
  {
    *(.data.trickbox)
  } > trickbox_mem

  .text.core_0_el3_root__code_segment_2_1304 0x8195a000 : AT(0x1bfad7000)
  {
    *(.text.core_0_el3_root__code_segment_2_1304)
  } > memory_region_core_0_el3_root

  .data.core_0_el3_root__data_shared_segment_0_1308 0x819a0000 : AT(0xa86f6000)
  {
    *(.data.core_0_el3_root__data_shared_segment_0_1308)
  } > memory_region_core_0_el3_root

  .text.core_0_el3_root__code_segment_5_1307 0x81e50c20 : AT(0x80250c20)
  {
    *(.text.core_0_el3_root__code_segment_5_1307)
  } > memory_region_core_0_el3_root

  .text.core_0_el3_root__code_segment_3_1305 0x81edca60 : AT(0x802dca60)
  {
    *(.text.core_0_el3_root__code_segment_3_1305)
  } > memory_region_core_0_el3_root

  .text.exception_table_core_0_el3_root_1347 0x81ee3000 : AT(0x802e3000)
  {
    *(.text.exception_table_core_0_el3_root_1347)
  } > memory_region_core_0_el3_root

  .text.core_0_el3_root__code_segment_1_1303 0x81f33c10 : AT(0x80333c10)
  {
    *(.text.core_0_el3_root__code_segment_1_1303)
  } > memory_region_core_0_el3_root

  .text.BSP__boot_segment_1296 0x82000000 : AT(0x82000000)
  {
    *(.text.BSP__boot_segment_1296)
    *(.text.boot*)
    *(.boot*)
  } > memory_region_core_0_el3_root

  .text.core_0_el3_root__boot_segment_1301 0x82000380 : AT(0x82000380)
  {
    *(.text.core_0_el3_root__boot_segment_1301)
  } > memory_region_core_0_el3_root

  .data.core_0_el3_root__data_preserve_segment_0_1310 0x8a3c4fe0 : AT(0x1f8bc4fe0)
  {
    *(.data.core_0_el3_root__data_preserve_segment_0_1310)
  } > memory_region_core_0_el3_root

  .text.core_0_el3_root__code_segment_0_1302 0xace22000 : AT(0xd5e6e000)
  {
    *(.text.core_0_el3_root__code_segment_0_1302)
  } > memory_region_core_0_el3_root

  .data.cross_core_data_segment_1297 0xe4e5aa80 : AT(0xd605aa80)
  {
    *(.data.cross_core_data_segment_1297)
  } > memory_region_core_0_el3_root

  .data.core_0_el3_root__data_preserve_segment_1_1311 0xe4fdd2d0 : AT(0xd61dd2d0)
  {
    *(.data.core_0_el3_root__data_preserve_segment_1_1311)
  } > memory_region_core_0_el3_root

  .text.core_0_el3_root__code_segment_4_1306 0x1310f1aa0 : AT(0x806f1aa0)
  {
    *(.text.core_0_el3_root__code_segment_4_1306)
  } > memory_region_core_0_el3_root

  .data.core_0_el3_root__data_shared_segment_1_1309 0x17cce0e40 : AT(0x14e4e0e40)
  {
    *(.data.core_0_el3_root__data_shared_segment_1_1309)
  } > memory_region_core_0_el3_root

  .stack 0x89688860 : AT(0x89688860)
  {
    *(.stack)
  } > memory_region_core_0_el3_root

  .data.core_0_el1_ns__data_shared_segment_0_1319 0x1ea001000 : AT(0x1d4509000)
  {
    *(.data.core_0_el1_ns__data_shared_segment_0_1319)
  } > memory_region_core_0_el1_ns

  .text.core_0_el1_ns__code_segment_0_1313 0x1ea3a1b00 : AT(0x1d69a1b00)
  {
    *(.text.core_0_el1_ns__code_segment_0_1313)
  } > memory_region_core_0_el1_ns

  .text.core_0_el1_ns__code_segment_3_1316 0x1ea470000 : AT(0xd5f47000)
  {
    *(.text.core_0_el1_ns__code_segment_3_1316)
  } > memory_region_core_0_el1_ns

  .text.core_0_el1_ns__code_segment_4_1317 0x1ea7c1000 : AT(0x1f9565000)
  {
    *(.text.core_0_el1_ns__code_segment_4_1317)
  } > memory_region_core_0_el1_ns

  .data.core_0_el1_ns__data_shared_segment_1_1320 0x1eabd7000 : AT(0x1d15d6000)
  {
    *(.data.core_0_el1_ns__data_shared_segment_1_1320)
  } > memory_region_core_0_el1_ns

  .text.core_0_el1_ns__code_segment_1_1314 0x1eb24a2c0 : AT(0x1d164a2c0)
  {
    *(.text.core_0_el1_ns__code_segment_1_1314)
  } > memory_region_core_0_el1_ns

  .data.cross_core_data_segment_1298 0x1eb45aa80 (NOLOAD) :
  {
    *(.data.cross_core_data_segment_1298)
  } > memory_region_core_0_el1_ns

  .data.core_0_el1_ns__data_preserve_segment_0_1321 0x1eb5ce070 : AT(0xd61ce070)
  {
    *(.data.core_0_el1_ns__data_preserve_segment_0_1321)
  } > memory_region_core_0_el1_ns

  .text.core_0_el1_ns__code_segment_5_1318 0x20670b790 : AT(0x1c030b790)
  {
    *(.text.core_0_el1_ns__code_segment_5_1318)
  } > memory_region_core_0_el1_ns

  .text.core_0_el1_ns__code_segment_2_1315 0x21f0f8000 : AT(0xd5f3a000)
  {
    *(.text.core_0_el1_ns__code_segment_2_1315)
  } > memory_region_core_0_el1_ns

  .data.core_0_el1_ns__data_preserve_segment_1_1322 0x2591c2000 : AT(0x1e7904000)
  {
    *(.data.core_0_el1_ns__data_preserve_segment_1_1322)
  } > memory_region_core_0_el1_ns

  .text.exception_table_core_0_el1_ns_1348 0x259c21800 : AT(0x221421800)
  {
    *(.text.exception_table_core_0_el1_ns_1348)
  } > memory_region_core_0_el1_ns

  .stack 0x2322d38a0 : AT(0x2322d38a0)
  {
    *(.stack)
  } > memory_region_core_0_el1_ns

  .data.core_1_el3_root__data_shared_segment_1_1332 0xaf557000 : AT(0x1c0412000)
  {
    *(.data.core_1_el3_root__data_shared_segment_1_1332)
  } > memory_region_core_1_el3_root

  .text.core_1_el3_root__code_segment_3_1328 0xafbc1220 : AT(0xae7c1220)
  {
    *(.text.core_1_el3_root__code_segment_3_1328)
  } > memory_region_core_1_el3_root

  .text.exception_table_core_1_el3_root_1349 0x11fa01800 : AT(0x1d4145800)
  {
    *(.text.exception_table_core_1_el3_root_1349)
  } > memory_region_core_1_el3_root

  .text.core_1_el3_root__code_segment_0_1325 0x1299a5000 : AT(0x1d552b000)
  {
    *(.text.core_1_el3_root__code_segment_0_1325)
  } > memory_region_core_1_el3_root

  .data.core_1_el3_root__data_shared_segment_0_1331 0x14455d700 : AT(0x1d0d5d700)
  {
    *(.data.core_1_el3_root__data_shared_segment_0_1331)
  } > memory_region_core_1_el3_root

  .data.cross_core_data_segment_1299 0x17285aa80 (NOLOAD) :
  {
    *(.data.cross_core_data_segment_1299)
  } > memory_region_core_1_el3_root

  .text.core_1_el3_root__code_segment_1_1326 0x1dfdaf8d0 : AT(0x1d35af8d0)
  {
    *(.text.core_1_el3_root__code_segment_1_1326)
  } > memory_region_core_1_el3_root

  .text.core_1_el3_root__code_segment_4_1329 0x204ba2210 : AT(0x1d47a2210)
  {
    *(.text.core_1_el3_root__code_segment_4_1329)
  } > memory_region_core_1_el3_root

  .data.core_1_el3_root__data_preserve_segment_0_1333 0x233ed83e0 : AT(0x1d7ed83e0)
  {
    *(.data.core_1_el3_root__data_preserve_segment_0_1333)
  } > memory_region_core_1_el3_root

  .text.core_1_el3_root__code_segment_5_1330 0x2395d5000 : AT(0x1e1472000)
  {
    *(.text.core_1_el3_root__code_segment_5_1330)
  } > memory_region_core_1_el3_root

  .text.core_1_el3_root__boot_segment_1324 0x27e5c3ad0 : AT(0x27e5c3ad0)
  {
    *(.text.core_1_el3_root__boot_segment_1324)
  } > memory_region_core_1_el3_root

  .data.core_1_el3_root__data_preserve_segment_1_1334 0x27e6d7eb0 : AT(0x2420d7eb0)
  {
    *(.data.core_1_el3_root__data_preserve_segment_1_1334)
  } > memory_region_core_1_el3_root

  .text.core_1_el3_root__code_segment_2_1327 0x27fec0080 : AT(0x1d1139080)
  {
    *(.text.core_1_el3_root__code_segment_2_1327)
  } > memory_region_core_1_el3_root

  .stack 0x1729a72e0 : AT(0x1729a72e0)
  {
    *(.stack)
  } > memory_region_core_1_el3_root

  .text.core_1_el1_ns__code_segment_4_1340 0x8960a560 : AT(0x1f7c0a560)
  {
    *(.text.core_1_el1_ns__code_segment_4_1340)
  } > memory_region_core_1_el1_ns

  .data.cross_core_data_segment_1300 0x91e5aa80 (NOLOAD) :
  {
    *(.data.cross_core_data_segment_1300)
  } > memory_region_core_1_el1_ns

  .text.core_1_el1_ns__code_segment_1_1337 0xf35839b0 : AT(0x14bb839b0)
  {
    *(.text.core_1_el1_ns__code_segment_1_1337)
  } > memory_region_core_1_el1_ns

  .text.core_1_el1_ns__code_segment_3_1339 0xf35c09e0 : AT(0x14bbc09e0)
  {
    *(.text.core_1_el1_ns__code_segment_3_1339)
  } > memory_region_core_1_el1_ns

  .text.core_1_el1_ns__code_segment_5_1341 0x115f657b0 : AT(0x1d37657b0)
  {
    *(.text.core_1_el1_ns__code_segment_5_1341)
  } > memory_region_core_1_el1_ns

  .text.core_1_el1_ns__code_segment_0_1336 0x191f097d0 : AT(0x1c01097d0)
  {
    *(.text.core_1_el1_ns__code_segment_0_1336)
  } > memory_region_core_1_el1_ns

  .text.exception_table_core_1_el1_ns_1350 0x191f37000 : AT(0x1c0137000)
  {
    *(.text.exception_table_core_1_el1_ns_1350)
  } > memory_region_core_1_el1_ns

  .data.core_1_el1_ns__data_preserve_segment_1_1345 0x1f00d3000 : AT(0xa3997000)
  {
    *(.data.core_1_el1_ns__data_preserve_segment_1_1345)
  } > memory_region_core_1_el1_ns

  .data.core_1_el1_ns__data_shared_segment_0_1342 0x27523f300 : AT(0x15043f300)
  {
    *(.data.core_1_el1_ns__data_shared_segment_0_1342)
  } > memory_region_core_1_el1_ns

  .text.core_1_el1_ns__code_segment_2_1338 0x277901000 : AT(0xa5190000)
  {
    *(.text.core_1_el1_ns__code_segment_2_1338)
  } > memory_region_core_1_el1_ns

  .data.core_1_el1_ns__data_preserve_segment_0_1344 0x280124da0 : AT(0xc1f24da0)
  {
    *(.data.core_1_el1_ns__data_preserve_segment_0_1344)
  } > memory_region_core_1_el1_ns

  .data.core_1_el1_ns__data_shared_segment_1_1343 0x2801f0600 : AT(0xc1ff0600)
  {
    *(.data.core_1_el1_ns__data_shared_segment_1_1343)
  } > memory_region_core_1_el1_ns

  .stack 0x27f6d69c0 : AT(0x27f6d69c0)
  {
    *(.stack)
  } > memory_region_core_1_el1_ns

  .data.pgt_constants 0x801c0000 : AT(0x801c0000)
  {
    *(.data.pgt_constants)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0 0x80000000 :
  {
    *(.data.el3_core_0_0_l0_0)
    *(.EL3_core_0_0_l0_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_0 0x80010000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_0)
    *(.EL3_core_0_0_l0_0_l1_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_0_l2_0 0x80020000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_0_l2_0)
    *(.EL3_core_0_0_l0_0_l1_0_l2_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_0 0x80030000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_0_l3_0 0x801d0000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_0_l3_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_0_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_12_l3_0 0x801f0000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_12_l3_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_12_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_14_l3_0 0x82030000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_14_l3_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_14_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_16_l3_0 0x82010000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_16_l3_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_16_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_30_l3_0 0x80040000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_30_l3_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_30_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_86_l3_0 0x82020000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_86_l3_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_86_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_2_l2_359_l3_0 0xd5e70000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_2_l2_359_l3_0)
    *(.EL3_core_0_0_l0_0_l1_2_l2_359_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_3_l2_0 0xd5e40000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_3_l2_0)
    *(.EL3_core_0_0_l0_0_l1_3_l2_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_4_l2_0 0x801e0000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_4_l2_0)
    *(.EL3_core_0_0_l0_0_l1_4_l2_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_4_l2_117_l3_0 0x80050000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_4_l2_117_l3_0)
    *(.EL3_core_0_0_l0_0_l1_4_l2_117_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_5_l2_0 0xa86e0000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_5_l2_0)
    *(.EL3_core_0_0_l0_0_l1_5_l2_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_5_l2_39_l3_0 0x80060000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_5_l2_39_l3_0)
    *(.EL3_core_0_0_l0_0_l1_5_l2_39_l3_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_6_l2_0 0xd5e50000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_6_l2_0)
    *(.EL3_core_0_0_l0_0_l1_6_l2_0)
  } > memory_region_utilities

  .data.el3_core_0_0_l0_0_l1_9_l2_0 0x80070000 :
  {
    *(.data.el3_core_0_0_l0_0_l1_9_l2_0)
    *(.EL3_core_0_0_l0_0_l1_9_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0 0xd5f20000 :
  {
    *(.data.el1ns_core_0_0_l0_0)
    *(.EL1NS_core_0_0_l0_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_0 0xa86c0000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_0)
    *(.EL1NS_core_0_0_l0_0_l1_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_5_l2_0 0xd5f60000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_5_l2_0)
    *(.EL1NS_core_0_0_l0_0_l1_5_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_7_l2_0 0xd5f10000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_7_l2_0)
    *(.EL1NS_core_0_0_l0_0_l1_7_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_7_l2_328_l3_0 0x80180000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_7_l2_328_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_7_l2_328_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_7_l2_336_l3_0 0x801b0000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_7_l2_336_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_7_l2_336_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_7_l2_338_l3_0 0xd5f50000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_7_l2_338_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_7_l2_338_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_7_l2_339_l3_0 0xbd420000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_7_l2_339_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_7_l2_339_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_7_l2_341_l3_0 0xd5f70000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_7_l2_341_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_7_l2_341_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_8_l2_0 0xa86d0000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_8_l2_0)
    *(.EL1NS_core_0_0_l0_0_l1_8_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_8_l2_230_l3_0 0x80190000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_8_l2_230_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_8_l2_230_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_8_l2_248_l3_0 0xd5f00000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_8_l2_248_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_8_l2_248_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_9_l2_0 0xbd410000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_9_l2_0)
    *(.EL1NS_core_0_0_l0_0_l1_9_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_9_l2_200_l3_0 0xbd430000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_9_l2_200_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_9_l2_200_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_0_0_l0_0_l1_9_l2_295_l3_0 0x801a0000 :
  {
    *(.data.el1ns_core_0_0_l0_0_l1_9_l2_295_l3_0)
    *(.EL1NS_core_0_0_l0_0_l1_9_l2_295_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0 0x82040000 :
  {
    *(.data.el3_core_1_0_l0_0)
    *(.EL3_core_1_0_l0_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_0 0x82050000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_0)
    *(.EL3_core_1_0_l0_0_l1_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_0_l2_0 0x82060000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_0_l2_0)
    *(.EL3_core_1_0_l0_0_l1_0_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_2_l2_0 0x82070000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_2_l2_0)
    *(.EL3_core_1_0_l0_0_l1_2_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_2_l2_0_l3_0 0xa8680000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_2_l2_0_l3_0)
    *(.EL3_core_1_0_l0_0_l1_2_l2_0_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_2_l2_378_l3_0 0xb2340000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_2_l2_378_l3_0)
    *(.EL3_core_1_0_l0_0_l1_2_l2_378_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_3_l2_0 0xa3230000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_3_l2_0)
    *(.EL3_core_1_0_l0_0_l1_3_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_3_l2_253_l3_0 0xb2370000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_3_l2_253_l3_0)
    *(.EL3_core_1_0_l0_0_l1_3_l2_253_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_3_l2_273_l3_0 0xbd450000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_3_l2_273_l3_0)
    *(.EL3_core_1_0_l0_0_l1_3_l2_273_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_3_l2_297_l3_0 0xa3200000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_3_l2_297_l3_0)
    *(.EL3_core_1_0_l0_0_l1_3_l2_297_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_4_l2_0 0xa3210000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_4_l2_0)
    *(.EL3_core_1_0_l0_0_l1_4_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_4_l2_58_l3_0 0xbd440000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_4_l2_58_l3_0)
    *(.EL3_core_1_0_l0_0_l1_4_l2_58_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_4_l2_253_l3_0 0xd5fc0000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_4_l2_253_l3_0)
    *(.EL3_core_1_0_l0_0_l1_4_l2_253_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_4_l2_272_l3_0 0xb2360000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_4_l2_272_l3_0)
    *(.EL3_core_1_0_l0_0_l1_4_l2_272_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_4_l2_274_l3_0 0xa3260000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_4_l2_274_l3_0)
    *(.EL3_core_1_0_l0_0_l1_4_l2_274_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_4_l2_332_l3_0 0xb2310000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_4_l2_332_l3_0)
    *(.EL3_core_1_0_l0_0_l1_4_l2_332_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_4_l2_426_l3_0 0xa3240000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_4_l2_426_l3_0)
    *(.EL3_core_1_0_l0_0_l1_4_l2_426_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_5_l2_0 0xd5ff0000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_5_l2_0)
    *(.EL3_core_1_0_l0_0_l1_5_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_7_l2_0 0xa3250000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_7_l2_0)
    *(.EL3_core_1_0_l0_0_l1_7_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_7_l2_361_l3_0 0xb2350000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_7_l2_361_l3_0)
    *(.EL3_core_1_0_l0_0_l1_7_l2_361_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_7_l2_436_l3_0 0xb2320000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_7_l2_436_l3_0)
    *(.EL3_core_1_0_l0_0_l1_7_l2_436_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_8_l2_0 0xa86a0000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_8_l2_0)
    *(.EL3_core_1_0_l0_0_l1_8_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_8_l2_392_l3_0 0xa86b0000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_8_l2_392_l3_0)
    *(.EL3_core_1_0_l0_0_l1_8_l2_392_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_8_l2_458_l3_0 0xd5fe0000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_8_l2_458_l3_0)
    *(.EL3_core_1_0_l0_0_l1_8_l2_458_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_8_l2_462_l3_0 0xa3270000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_8_l2_462_l3_0)
    *(.EL3_core_1_0_l0_0_l1_8_l2_462_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_9_l2_0 0xa8690000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_9_l2_0)
    *(.EL3_core_1_0_l0_0_l1_9_l2_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_9_l2_511_l3_0 0xb2300000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_9_l2_511_l3_0)
    *(.EL3_core_1_0_l0_0_l1_9_l2_511_l3_0)
  } > memory_region_utilities

  .data.el3_core_1_0_l0_0_l1_10_l2_0 0xbd460000 :
  {
    *(.data.el3_core_1_0_l0_0_l1_10_l2_0)
    *(.EL3_core_1_0_l0_0_l1_10_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0 0xbd470000 :
  {
    *(.data.el1ns_core_1_0_l0_0)
    *(.EL1NS_core_1_0_l0_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_0 0xd5e00000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_0)
    *(.EL1NS_core_1_0_l0_0_l1_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_2_l2_0 0xd5f80000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_2_l2_0)
    *(.EL1NS_core_1_0_l0_0_l1_2_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_3_l2_0 0xd5e30000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_3_l2_0)
    *(.EL1NS_core_1_0_l0_0_l1_3_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_4_l2_0 0xd5f90000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_4_l2_0)
    *(.EL1NS_core_1_0_l0_0_l1_4_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_4_l2_187_l3_0 0x80080000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_4_l2_187_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_4_l2_187_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_6_l2_0 0xd5e10000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_6_l2_0)
    *(.EL1NS_core_1_0_l0_0_l1_6_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_6_l2_101_l3_0 0xd5fa0000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_6_l2_101_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_6_l2_101_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_6_l2_130_l3_0 0xa5180000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_6_l2_130_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_6_l2_130_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_7_l2_0 0x800b0000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_7_l2_0)
    *(.EL1NS_core_1_0_l0_0_l1_7_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_7_l2_384_l3_0 0xa3980000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_7_l2_384_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_7_l2_384_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_9_l2_0 0xd5e20000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_9_l2_0)
    *(.EL1NS_core_1_0_l0_0_l1_9_l2_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_9_l2_419_l3_0 0x800a0000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_9_l2_419_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_9_l2_419_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_9_l2_431_l3_0 0xd5fb0000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_9_l2_431_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_9_l2_431_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_9_l2_440_l3_0 0xa39a0000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_9_l2_440_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_9_l2_440_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_9_l2_444_l3_0 0x80090000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_9_l2_444_l3_0)
    *(.EL1NS_core_1_0_l0_0_l1_9_l2_444_l3_0)
  } > memory_region_utilities

  .data.el1ns_core_1_0_l0_0_l1_10_l2_0 0xa39b0000 :
  {
    *(.data.el1ns_core_1_0_l0_0_l1_10_l2_0)
    *(.EL1NS_core_1_0_l0_0_l1_10_l2_0)
  } > memory_region_utilities

}
