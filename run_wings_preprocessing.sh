./coresyf_calibration.py --Ttarget image_calibrated --Ssource S1B_IW_GRDH_1SDV_20170724T064228_20170724T064253_006626_00BA71_D464.zip
./coresyf_speckle_filter.py --Ttarget image_filtered -s image_calibrated


./Tiling.py -i ./image_filtered -b ./lnec_grid_preprocessing.txt -a config_file.ini -s 0.5 -u tile-zip-1 tile-zip-2 tile-zip-3 tile-zip-4 tile-zip-5 tile-zip-6 tile-zip-7 tile-zip-8 tile-zip-9 tile-zip-10 tile-zip-11 tile-zip-12 tile-zip-13 tile-zip-14 tile-zip-15 tile-zip-16 tile-zip-17 tile-zip-18 tile-zip-19 tile-zip-20 tile-zip-21 tile-zip-22 tile-zip-23 tile-zip-24 tile-zip-25 tile-zip-26 tile-zip-27 tile-zip-28 tile-zip-29 tile-zip-30 tile-zip-31 tile-zip-32 tile-zip-33 tile-zip-34 tile-zip-35 tile-zip-36 tile-zip-37 tile-zip-38 tile-zip-39 tile-zip-40 tile-zip-41 tile-zip-42 tile-zip-43 tile-zip-44 tile-zip-45 tile-zip-46 tile-zip-47 tile-zip-48 tile-zip-49 tile-zip-50 tile-zip-51 tile-zip-52 tile-zip-53 tile-zip-54 tile-zip-55 tile-zip-56 tile-zip-57 tile-zip-58 tile-zip-59 tile-zip-60 tile-zip-61 tile-zip-62 tile-zip-63 tile-zip-64 tile-zip-65 tile-zip-66 tile-zip-67 tile-zip-68 tile-zip-69 tile-zip-70 tile-zip-71 tile-zip-72 tile-zip-73 tile-zip-74 tile-zip-75 tile-zip-76 tile-zip-77 tile-zip-78 tile-zip-79 tile-zip-80 tile-zip-81 tile-zip-82 tile-zip-83 tile-zip-84 tile-zip-85 tile-zip-86 tile-zip-87 tile-zip-88 tile-zip-89 tile-zip-90 tile-zip-91 tile-zip-92 tile-zip-93 tile-zip-94 tile-zip-95 tile-zip-96 tile-zip-97 tile-zip-98 tile-zip-99 tile-zip-100 tile-zip-101 tile-zip-102 tile-zip-103 tile-zip-104 tile-zip-105 tile-zip-106 tile-zip-107 tile-zip-108 tile-zip-109 tile-zip-110

./FFT_bath.py -i tile-zip-1 -o textfilebath_1.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-2 -o textfilebath_2.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-3 -o textfilebath_3.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-4 -o textfilebath_4.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-5 -o textfilebath_5.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-6 -o textfilebath_6.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-7 -o textfilebath_7.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-8 -o textfilebath_8.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-9 -o textfilebath_9.txt -a config_file.ini -t 13 
./FFT_bath.py -i tile-zip-10 -o textfilebath_10.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-11 -o textfilebath_11.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-12 -o textfilebath_12.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-13 -o textfilebath_13.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-14 -o textfilebath_14.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-15 -o textfilebath_15.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-16 -o textfilebath_16.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-17 -o textfilebath_17.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-18 -o textfilebath_18.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-19 -o textfilebath_19.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-20 -o textfilebath_20.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-21 -o textfilebath_21.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-22 -o textfilebath_22.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-23 -o textfilebath_23.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-24 -o textfilebath_24.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-25 -o textfilebath_25.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-26 -o textfilebath_26.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-27 -o textfilebath_27.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-28 -o textfilebath_28.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-29 -o textfilebath_29.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-30 -o textfilebath_30.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-31 -o textfilebath_31.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-32 -o textfilebath_32.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-33 -o textfilebath_33.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-34 -o textfilebath_34.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-35 -o textfilebath_35.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-36 -o textfilebath_36.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-37 -o textfilebath_37.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-38 -o textfilebath_38.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-39 -o textfilebath_39.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-40 -o textfilebath_40.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-41 -o textfilebath_41.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-42 -o textfilebath_42.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-43 -o textfilebath_43.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-44 -o textfilebath_44.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-45 -o textfilebath_45.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-46 -o textfilebath_46.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-47 -o textfilebath_47.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-48 -o textfilebath_48.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-49 -o textfilebath_49.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-50 -o textfilebath_50.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-51 -o textfilebath_51.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-52 -o textfilebath_52.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-53 -o textfilebath_53.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-54 -o textfilebath_54.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-55 -o textfilebath_55.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-56 -o textfilebath_56.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-57 -o textfilebath_57.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-58 -o textfilebath_58.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-59 -o textfilebath_59.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-60 -o textfilebath_60.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-61 -o textfilebath_61.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-62 -o textfilebath_62.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-63 -o textfilebath_63.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-64 -o textfilebath_64.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-65 -o textfilebath_65.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-66 -o textfilebath_66.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-67 -o textfilebath_67.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-68 -o textfilebath_68.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-69 -o textfilebath_69.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-70 -o textfilebath_70.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-71 -o textfilebath_71.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-72 -o textfilebath_72.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-73 -o textfilebath_73.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-74 -o textfilebath_74.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-75 -o textfilebath_75.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-76 -o textfilebath_76.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-77 -o textfilebath_77.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-78 -o textfilebath_78.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-79 -o textfilebath_79.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-80 -o textfilebath_80.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-81 -o textfilebath_81.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-82 -o textfilebath_82.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-83 -o textfilebath_83.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-84 -o textfilebath_84.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-85 -o textfilebath_85.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-86 -o textfilebath_86.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-87 -o textfilebath_87.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-88 -o textfilebath_88.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-89 -o textfilebath_89.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-90 -o textfilebath_90.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-91 -o textfilebath_91.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-92 -o textfilebath_92.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-93 -o textfilebath_93.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-94 -o textfilebath_94.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-95 -o textfilebath_95.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-96 -o textfilebath_96.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-97 -o textfilebath_97.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-98 -o textfilebath_98.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-99 -o textfilebath_99.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-100 -o textfilebath_100.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-101 -o textfilebath_101.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-102 -o textfilebath_102.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-103 -o textfilebath_103.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-104 -o textfilebath_104.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-105 -o textfilebath_105.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-106 -o textfilebath_106.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-107 -o textfilebath_107.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-108 -o textfilebath_108.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-109 -o textfilebath_109.txt -a config_file.ini -t 13
./FFT_bath.py -i tile-zip-110 -o textfilebath_110.txt -a config_file.ini -t 13


./Merge.py -i textfilebath_1.txt textfilebath_2.txt textfilebath_3.txt textfilebath_4.txt textfilebath_5.txt textfilebath_6.txt textfilebath_7.txt textfilebath_8.txt textfilebath_9.txt textfilebath_10.txt textfilebath_11.txt textfilebath_12.txt textfilebath_13.txt textfilebath_14.txt textfilebath_15.txt textfilebath_16.txt textfilebath_17.txt textfilebath_18.txt textfilebath_19.txt textfilebath_20.txt textfilebath_21.txt textfilebath_22.txt textfilebath_23.txt textfilebath_24.txt textfilebath_25.txt textfilebath_26.txt textfilebath_27.txt textfilebath_28.txt textfilebath_29.txt textfilebath_30.txt textfilebath_31.txt textfilebath_32.txt textfilebath_33.txt textfilebath_34.txt textfilebath_35.txt textfilebath_36.txt textfilebath_37.txt textfilebath_38.txt textfilebath_39.txt textfilebath_40.txt textfilebath_41.txt textfilebath_42.txt textfilebath_43.txt textfilebath_44.txt textfilebath_45.txt textfilebath_46.txt textfilebath_47.txt textfilebath_48.txt textfilebath_49.txt textfilebath_50.txt textfilebath_51.txt textfilebath_52.txt textfilebath_53.txt textfilebath_54.txt textfilebath_55.txt textfilebath_56.txt textfilebath_57.txt textfilebath_58.txt textfilebath_59.txt textfilebath_60.txt textfilebath_61.txt textfilebath_62.txt textfilebath_63.txt textfilebath_64.txt textfilebath_65.txt textfilebath_66.txt textfilebath_67.txt textfilebath_68.txt textfilebath_69.txt textfilebath_70.txt textfilebath_71.txt textfilebath_72.txt textfilebath_73.txt textfilebath_74.txt textfilebath_75.txt textfilebath_76.txt textfilebath_77.txt textfilebath_78.txt textfilebath_79.txt textfilebath_80.txt textfilebath_81.txt textfilebath_82.txt textfilebath_83.txt textfilebath_84.txt textfilebath_85.txt textfilebath_86.txt textfilebath_87.txt textfilebath_88.txt textfilebath_89.txt textfilebath_90.txt textfilebath_91.txt textfilebath_92.txt textfilebath_93.txt textfilebath_94.txt textfilebath_95.txt textfilebath_96.txt textfilebath_97.txt textfilebath_98.txt textfilebath_99.txt textfilebath_100.txt textfilebath_101.txt textfilebath_102.txt textfilebath_103.txt textfilebath_104.txt textfilebath_105.txt textfilebath_106.txt textfilebath_107.txt textfilebath_108.txt textfilebath_109.txt textfilebath_110.txt -o bathymetry.txt

./coresyf_vector_creator_lnec_wings.py -o myshapefile --data_file bathymetry.txt 
./coresyf_pointsToGrid_lnec_wings.py -s myshapefile --s_field="Depth" -a nearest -o myrasterfile.tiff