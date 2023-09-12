{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# CURRENT CLICK \n",
    "\n",
    "**Setup code**\n",
    "\n",
    "Imports the Mercury overlay from the Red Pitaya library and gives it an alias \"FPGA\". Creates an object called \"overlay\" which represents the Mercury overlay on the Red Pitaya board."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from redpitaya.overlay.mercury import mercury as FPGA\n",
    "import time\n",
    "\n",
    "# Initialize the FPGA overlay\n",
    "overlay = FPGA()\n",
    "\n",
    "LED = FPGA.led\n",
    "\n",
    "mikrobus1AinPin = FPGA.analog_in(0)\n",
    "mikrobus2AinPin = FPGA.analog_in(1)\n",
    "\n",
    "def convert_to_engineering_unit(number, units):\n",
    "    magnitude = number\n",
    "    unit_index = 0\n",
    "\n",
    "    while magnitude <= 1.0 and unit_index < len(units) - 1:\n",
    "        magnitude *= 1000.0\n",
    "        unit_index += 1\n",
    "\n",
    "    print(\"Value: {:.4f} {} \\n\".format(magnitude, units[unit_index]))\n",
    "\n",
    "def get_current(pin, resistor_value):\n",
    "    # Get ADC value from the specified pin\n",
    "    value = pin.read()\n",
    "    max_current = 3.3 / (20.0 * resistor_value)\n",
    "    print(\"Minimum current is 2mA, maximum is:\")\n",
    "    convert_to_engineering_unit(max_current, [\"A\", \"mA\", \"μA\", \"nA\"])\n",
    "\n",
    "    # Calculate current\n",
    "    voltage = value / 20.0\n",
    "    # gain of circuit is 20\n",
    "    current = voltage / resistor_value\n",
    "\n",
    "    return current\n",
    "\n",
    "def recommend_resistor(current):\n",
    "    if current != 0:\n",
    "        resistor = 0.075 / current\n",
    "        print(\"The recommended resistor value for best measurement (R) is {:.4f} ohms.\\n\".format(resistor))\n",
    "        return resistor\n",
    "    else:\n",
    "        print(\"Error: Current (I) cannot be zero.\\n\")\n",
    "        return -1\n",
    "        # Return -1 to indicate an error"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The example shows how to read the current through a shunt resistor. The program, however, does not know how many ohms your shunt resistor has. That is why the shunt resistor value must be input when prompted by the program. Also, the shunt resistor should be accurate to at least three decimals (for example, with a multimeter). That way, the current measurement will be most accurate.\n",
    "\n",
    "Refrain from going above or below the minimum and maximum current measurement.\n",
    "\n",
    "For best measurements, please use the recommended resistor."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "while True:\n",
    "    print(\"Enter shunt resistor value in Ohms: \")\n",
    "    # circuit 5 ohms\n",
    "    resistor_value = float(input())\n",
    "    current = get_current(mikrobus1AinPin, resistor_value)\n",
    "\n",
    "    convert_to_engineering_unit(current, [\"A\", \"mA\", \"μA\", \"nA\"])\n",
    "    recommend_resistor(current)\n",
    "    time.sleep(1)"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  },
  "orig_nbformat": 4
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
