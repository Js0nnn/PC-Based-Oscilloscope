#include "ADS1X15.h"

ADS1115 ADS(0x48);

const float voltageDividerFactor = 11.9; // Refined factor by which the voltage divider scales down the input voltage
const float virtualGround = 2.50; // Virtual ground reference provided by the op-amp
const float referenceVoltage = 5.0; // Reference voltage of the Arduino (adjust if using 3.3V or other reference)
const int adcMaxValue = 1023; // Maximum value for a 10-bit ADC

void setup() 
{
  Serial.begin(115200);
  Serial.println(__FILE__);
  Serial.print("ADS1X15_LIB_VERSION: ");
  Serial.println(ADS1X15_LIB_VERSION);

  ADS.begin();
  
  // Set analog reference to default (usually 5V or 3.3V, adjust if needed)
  analogReference(DEFAULT);
}

void loop() 
{
  ADS.setGain(1);
  /*
  0: GAIN_TWOTHIRDS (±6.144V)
  1: GAIN_ONE (±4.096V)
  2: GAIN_TWO (±2.048V)
  4: GAIN_FOUR (±1.024V)
  8: GAIN_EIGHT (±0.512V)
  16: GAIN_SIXTEEN (±0.256V)
  */

  int16_t val_0 = ADS.readADC(0);  
  int16_t val_1 = ADS.readADC(1);

  float f = ADS.toVoltage(1);  // voltage factor
  float measuredVoltage_0 = val_0 * f;
  float measuredVoltage_1 = val_1 * f;


  float adjustedVoltage_0 = (measuredVoltage_0 - virtualGround) * voltageDividerFactor;
  float adjustedVoltage_1 = (measuredVoltage_1 - virtualGround) * voltageDividerFactor;


  //Serial.print("Analog0: "); Serial.print(val_0); Serial.print('\t'); Serial.print(measuredVoltage_0, 3); Serial.print(" V (adjusted: "); Serial.print(adjustedVoltage_0, 3); Serial.print(" V) ");
  Serial.print("A0: "); Serial.print(adjustedVoltage_0, 3);
  //Serial.print("Analog1: "); Serial.print(val_1); Serial.print('\t'); Serial.print(measuredVoltage_1, 3); Serial.print(" V (adjusted: "); Serial.print(adjustedVoltage_1, 3); Serial.print(" V) ");
  Serial.print("  A1: "); Serial.println(adjustedVoltage_1, 3);


  //delay(1000);
}
