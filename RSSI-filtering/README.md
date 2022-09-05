# RSSI Filtering
The repository shows how to apply different filters to a data set of RSSI values.

The notebook folder contains three jupyter notebook that guides you from the data preparation and exploration phase through the resampling and finally the application of the filter.

Three filters have been developed and used:
- grey filter;
- Kalman filter;
- Fourier filter;
- particle filter.

The [PDF](https://github.com/peppekristen/RSSI_Filtering/blob/main/Improving_Indoor_Localization_using_Filtering.pdf) explains the context of application and goes deeply into the datails of the project.

The [dataset folder](https://github.com/peppekristen/RSSI_Filtering/tree/main/dataset) contains the raw data used, the clean data produced by the Preliminary Phase, and the resample data produced by the Resampling.

## References

The original filters implementations can be found [here](https://github.com/phillipiv/rssi-filtering-kalman).

The data set used can be found [here](https://archive.ics.uci.edu/ml/datasets/BLE+RSSI+dataset+for+Indoor+localization).

Other references:

[1] H. Liu, H. Darabi, P. Banerjee, and J. Liu, “Survey of wireless indoor positioning techniques
and systems,” IEEE Transactions on Systems, Man and Cybernetics Part C: Applications and Re-
views, vol. 37, no. 6, pp. 1067–1080, 2007.

[2] P. Bellavista, A. Corradi, and C. Giannelli, “Evaluating filtering strategies for decentralized
handover prediction in the wireless internet,” 11th IEEE Symposium on Computers and Commu-
nications (ISCC’06), pp. 167–174, 2006.

[3] A. Mussina and S. Aubakirov, “Rssi based bluetooth low energy indoor positioning,” 2018
IEEE 12th International Conference on Application of Information and Communication Technologies
(AICT), pp. 1–4, 2018.

[4] E. Kayacan, B. Ulutas, and O. Kaynak, “Grey system theory-based models in time series pre-
diction,” Expert Systems with Applications, vol. 37, pp. 1784–1789, 03 2010.

[5] M. Laaraiedh, “Implementation of kalman filter with python language,” The Python Papers,
2012.
