{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# LIGHT CLICK \n",
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
    "# by changing 1 to 2 in the code below you can use the second microbus"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The example measures light intensity by reading the analog value and displays whether it is light or dark. By covering the sensor or turning off the lights, the program is forced to output that it is dark."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "while True:\n",
    "    # Get light value\n",
    "    value = mikrobus1AinPin.read()\n",
    "    print(\"Measured voltage on AI[{}] = {}V\\n\".format(0, value))\n",
    "    if value >= 2.0:\n",
    "        # Turn on light based on button value\n",
    "        LED(0, 1).write(1)\n",
    "        print(\"There is LIGHT\\n\")\n",
    "    elif value <= 0.5:\n",
    "        # Turn off light based on button value\n",
    "        LED(0, 1).write(0)\n",
    "        print(\"There is no light\\n\")\n",
    "    else:\n",
    "        print(\"There is some light\\n\")\n",
    "\n",
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
