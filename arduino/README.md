# Serial Communication - Part I

<img align="left" src="https://img.shields.io/badge/Development Environment-Arduino-blue"><img align="left" src="https://img.shields.io/badge/Estimated Duration-2 h-green"></br>

In the previous practice, we used serial communication to send data from the microcontroller to the computer, but we did it as a "leap of faith," without knowing how it works or what we were doing. In this practice, we will start to see **how to operate** with serial communications and **what we are actually sending**.

There are multiple types of serial communications: [I<sup>2</sup>C (_Inter-Integrated Circuit_)](https://en.wikipedia.org/wiki/I²C), [SPI (_Serial Peripheral Interface_)](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface), [CAN (_Controller Area Network_)](https://en.wikipedia.org/wiki/CAN_bus), [UART (_Universal Asynchronous Receiver-Transmitter_)](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter), [PCIe (_Peripheral Component Interconnect Express_)](https://en.wikipedia.org/wiki/PCI_Express), [USB (_Universal Serial Bus_)](https://en.wikipedia.org/wiki/USB), [Ethernet](https://en.wikipedia.org/wiki/Ethernet),... Of all of them, in this practice, **we will see UART serial communication**. This is one of the simplest serial communications and one of the first to be introduced. It is common, and it is our case, that an EVB also contains a UART to USB converter so that, **through UART, we can send data to a computer via a USB connection**. Therefore, it is usually one of the first serial communications to learn. That, and because it is one of the most well-known communications.

### Serial vs Parallel

Okay, okay,... But let's start by seeing **what a serial communication is** and how it differs from the other type of communication called parallel. It's very simple. The terms serial and parallel refer to the **way bits are sent between devices**. In the case of **parallel communication**, **more than one bit is sent simultaneously** from one device to another. This means that at least one communication line per bit is needed (greater use of pins). But it has the advantage of higher transmission speed as more than one bit can be sent at a time.

![](/.github/images/parallel-communication.png)

> Image of a parallel communication. [[Source](https://learn.sparkfun.com/tutorials/serial-communication/all)]

On the other hand, in a **serial communication** **we send the bits individually in a sequential manner**. One after another. In this way, we reduce the number of necessary lines (and consequently, the number of necessary pins), but at the cost of a lower communication speed.

![](/.github/images/serial-communication.png)

> Image of a serial communication. [[Source](https://learn.sparkfun.com/tutorials/serial-communication/all)]

### Synchronous vs Asynchronous

**Another classification** for communications is whether they are synchronous or asynchronous. The **difference between them** is whether or not a clock signal is used to synchronize the sending of bits. A **synchronous communication**, in addition to sending the bits, will also **send a clock signal** to synchronize the writing/reading of the bits between devices. An **asynchronous communication** **does not need** that **clock signal** and we save a pin. Obviously, at the electronics level (not at the programming level, which is what we will see), it implies greater complexity that will be transparent to us.

### UART

Earlier we mentioned **UART as a serial communication** when **it is not strictly speaking**. **UART is the peripheral** responsible for carrying out the serial communication. In fact, in our microcontroller, the "UART" module is called **USART** (_Universal Synchronous/Asynchronous Receiver Transmitter_) since the peripheral can be configured to perform **synchronous and asynchronous communications**. So what we will see is simply an asynchronous serial communication. "And why are you deceiving us? What have we done to you!?" Nooo... Calm down. We will refer to asynchronous serial communication as UART since it is very common to refer to this communication by its peripheral, and in this way, you can more easily find documentation and information about this communication. In this practice, when we talk about UART, serial communication, or simply communication, we will be talking about asynchronous serial communication.

#### Connection

The connection is simple. Each device will have **three pins dedicated to communication**:

- **TX:** Pin dedicated to sending bits.
- **RX:** Pin dedicated to receiving bits.
- **GND:** Reference voltage that the devices must share.

For communication between two devices, **the TX of one must be connected to the RX** of the other and **vice versa**. The connection would look like this:

![](/.github/images/connection.png)

> Image of interconnection for a serial communication. [[Source](https://learn.sparkfun.com/tutorials/serial-communication/all)]

Although it is possible to connect **more than two devices** on the same asynchronous serial communication bus, **it is not usually recommended** since it requires taking a series of measures outside the "standard" to avoid communication conflicts on the bus.

> [!NOTE]
> A data bus is simply the logical grouping of all the signals involved in the communication.

#### Communication Parameters and Bit Framing

For asynchronous serial communication, we need to consider four essential parameters:

- **Number of data bits:** the number of data bits we will send per bit packet. These can be from 5 to 9, with 8 bits (1 byte) being the most common.
- **Number of synchronization bits:** the number of bits used to detect the start and end of a bit packet. There will always be an initial synchronization bit. We must choose whether to enable one or two synchronization bits at the end of the packet, also known as stop bits. It is common to use only one stop bit. The TX line is always at a high level when no transmission is taking place. In this state, it is said to be in the IDLE state. The synchronization bits are responsible for transitioning from IDLE to `0` when the transmission of a bit packet begins and from `0` to IDLE when it ends.
- **Enabling/disabling the parity bit:** a parity bit can be enabled or not, adding a simple error control to the communication. This parameter can be configured as _none_, _even_, or _odd_. If configured as _none_, there will be no parity bit. When configured as _even_, if the number of `1`s in the data bits is even, the parity bit will be 1. When configured as _odd_, if the number of `1`s in the data bits is odd, the parity bit will be 1.
- **_Baud rate_:** [symbol transmission speed](https://en.wikipedia.org/wiki/Baud). In this case, we take the bit as the symbol, so the _baud rate_ and the _bit rate_ coincide. This speed, indicated as bps (_bits per second_), can take any value. However, common speeds are: 1200, 2400, 4800, 9600, 19200, 38400, 57600, and 115200 bps. The most common is usually 9600 bps. The maximum is also usually 115200 bps (beyond that, the number of bits that can be lost along the way can be considerable, and error management would be necessary). Knowing the _baud rate_, we can calculate how long it would take to transmit a bit packet.

![](/.github/images/bit-framing.png)

> Image of bit framing for a serial communication. [[Source](https://learn.sparkfun.com/tutorials/serial-communication/all)]

It is common to refer to an asynchronous serial communication with a nomenclature generated from the communication parameters. For example, 9600 8N1 means: a _baud rate_ of 9600, with 8 data bits, no parity, and one stop bit. Another example would be 115200 5O2, which corresponds to: a baud rate of 115200 bps, 5 data bits, an odd parity bit, and two stop bits.

> [!WARNING]
> In this practice, we will talk a lot about bit packets or bit framing. It is important to emphasize **bits** because in the next practice, we will talk about byte packets or byte framing, which is very different.

With all the theory reviewed, let's work with asynchronous serial communication! 💪🏻

## Objectives

- Introduction to serial communication in Arduino.
- ASCII encoding.
- Sending RAW data.
- Switch statement.

## Procedure

### Installing CoolTerm

Before starting, we are going to **download and install** the **CoolTerm** application on our computer. You can find it **[here](https://freeware.the-meiers.org/)**. This application, available for Windows, Mac, and Linux, is a serial terminal like the one in VS Code, but with some interesting features that will help us see what we are sending in the serial communication.

### ASCII Encoding

Let's look at a basic aspect that we use every day but is masked when sending data via text: ASCII encoding.

#### "Hello, I am STM32"

Before going into detail about what it is, let's create a small project in PlatformIO that sends a text like **"Hello, I am STM32."** via **serial communication**. To do this, starting from the `main` branch, create a branch named `arduino/<username>/serial-ascii`, and create a project named `serial-ascii` (create it inside the folder named after your username within the workspace).

To perform serial communication in Arduino, we have the **library/object [`Serial`](https://www.arduino.cc/reference/en/language/functions/communication/serial/)**. To configure the **_baud rate_ of the communication**, we use the **`Serial.begin()`** function, where the _baud rate_ is specified as a parameter. By default, the communication is configured as `<baud rate>` 8N1, where `<baud rate>` is the value we have configured. Let's **initialize** the serial communication to **9600 8N1**.

```c++
#include <Arduino.h>

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // 9600 8N1
}

void loop()
{
  // put your main code here, to run repeatedly:
}
```

Now, let's make it so that the **message** "Hello, I am STM32." is sent **every time we press the button**. The code would look like this:

```c++
#include <Arduino.h>

#define BUTTON 23

void hello(void);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); // 9600 8N1

  pinMode(BUTTON, INPUT); // input mode
  // ISR configuration
  attachInterrupt(digitalPinToInterrupt(BUTTON), hello, FALLING);
}

void loop() {
  // put your main code here, to run repeatedly:

}

void hello(void) {
  // ISR button
  Serial.print("Hello, I am STM32."); // send message
}
```

With the `Serial.print()` function, we send a message/text via serial communication. We compile and upload the program to the microcontroller. Let's configure CoolTerm to receive those messages.

#### Configuring CoolTerm

We open the application, and the first thing we do is click on the **`Options` icon**. In this window, we can configure multiple parameters of the communication and the terminal, but we will only configure one thing for now: the port. **Select the appropriate port** for our EVB. If your EVB does not appear, click on `Re-Scan Serial Ports`.

> [!TIP]
> Remember that in Windows, it will take the value `COMX`, and in Mac/Linux, `usbmodemXXXX`.

Once selected, we leave the default configuration.

![](/.github/images/coolterm-config.png)

We can click on the `Save` icon to save the configuration. With everything configured, **click on the `Connect` button**. We test **sending a message by pressing the button** on our EVB, and **we should receive a "Hello, I am STM32."** for each press.

We can see that **the text is concatenated** without creating new lines for each message. That is because we used the `Serial.print()` function, which sends the text as is. If we use the **`Serial.println()` function, it sends the text** and then **adds two more characters**: a **carriage return** and a **new line** character. The first corresponds to the `\r` character, and the second to the `\n` character. Let's replace the `Serial.print()` function with `Serial.println()` in our _sketch_. It would look like this:

```diff
#include <Arduino.h>

#define BUTTON 23

void hello(void);

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // 9600 8N1

  pinMode(BUTTON, INPUT); // input mode
  // ISR configuration
  attachInterrupt(digitalPinToInterrupt(BUTTON), hello, FALLING);
}

void loop()
{
  // put your main code here, to run repeatedly:
}

void hello(void)
{
  // ISR button
+  Serial.println("Hello, I am STM32."); // send message
}
```

We compile, upload, and press the button. Now, **CoolTerm identifies the end of a message** by finding the `\r` and `\n` characters and **creates a new line**.

What we just used are delimiter characters or _term chars_. These indicate where a message ends.

#### But... What are we sending?

CoolTerm has a very interesting feature that lets us see **what we are actually sending**. It allows us to see the **raw data**. This feature is activated by clicking on the **`View HEX` icon**. When clicked, the terminal shows three columns.

We start with the **second column**. This shows **in hexadecimal the bit packets sent**. This is what we are actually sending. They are the **raw data**. By default, it shows 16 bit packets per row.

The **first column** is simply a **numbering that CoolTerm does** to identify each bit packet sent. The value in the column identifies the first bit packet of the 16 packets represented in the second column of that row.

Finally, the **third column** is the **ASCII encoding** of the raw values actually sent, which appear in the second column. And here we get to the crux of the matter: **when sending strings from the microcontroller, we are not sending text; we are sending numbers that are encoded in ASCII by the computer**. In the following table, you can see the ASCII encoding of the first 128 characters.

![](/.github/images/ascii-table.png)

> ASCII Encoding. [[Source](https://commons.wikimedia.org/wiki/File:ASCII-Table.svg)]

So when we send an `A`, we are actually sending a `65`. When we send an `f`, we are sending a `102`. And so on. Therefore, to send "Hello, I am STM32.", we are sending `72 101 108 108 111 44 32 73 32 97 109 32 83 84 77 51 50 46` in decimal or `0x48 0x65 0x6C 0x6C 0x6F 0x2C 0x20 0x49 0x20 0x61 0x6D 0x20 0x53 0x54 0x4D 0x33 0x32 0x2E` in hexadecimal.

> [!NOTE]
> When programming microcontrollers, to indicate that a number is being represented in hexadecimal, `0x` is placed in front of the number.
>
> If anyone does not know what a hexadecimal number is or how to obtain it, you can find more info [here](https://en.wikipedia.org/wiki/Hexadecimal).

"Okay, so what?" Well, imagine we want to send a number stored in a one-byte variable, that is, a `uint8_t` variable. That variable can take a maximum value of 255. If we send this number in ASCII encoding, we would have to send `0x32 0x35 0x35`; three bytes. If we send it in raw, we would have to send `0xFF`; just one byte. Do you see what happened? By using ASCII encoding, we had to use three bytes instead of just one. **ASCII encoding adds overhead** of two bytes. This significantly limits the communication bandwidth and would be unfeasible in applications where fast communication is needed. So, **_rule of thumb_**:

- Always use **raw data communication** and you will never have problems, and no one will look at you funny 😎
- If your application does not require fast transmission or a lot of data (and you don't care what people think of you... 🤪), you can use ASCII.

Remember, in real applications, we will never send text; we will always send numerical values and instructions or status variables encoded in numerical values, so there is little or no sense in using ASCII to send data.

> [!NOTE]
> When I talk about encoding instructions or status variables in numerical values, I mean that, for example, when I want to tell a device from the computer to start a measurement, I will not send "Please, when you have time, start measuring the pH of this sample." Instead, I will send, for example, `0x01`. And if I want it to stop, I will send `0x02` and not "Stop, stop, you're messing it up."
>
> **The choice of how each instruction is encoded is ours and is part of the process of designing the instruction set of our device.**

Check that it works correctly. If so, make a commit, push your changes, and create a Pull Request to the main branch. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request.

### Raw Data

We have seen that **ASCII is evil** and we must stay away from it. We won't even waste time seeing an example of how to send data from the computer to the microcontroller in ASCII. We will see it directly in raw.

> [!NOTE]
> For purists and nitpickers: note that when I say ASCII is evil and must be avoided, etc., its use obviously depends on the context and trade-off decisions made during solution design. Things are exaggerated here slightly to emphasize the overhead problem caused by using ASCII compared to raw data.

#### Sending Raw Data

To send data in raw, we forget about the `Serial.print()` function and use **the `Serial.write()`** function. The application to send a `1` would look like this:

```c++
#include <Arduino.h>

#define BUTTON 23

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // 9600 8N1

  pinMode(BUTTON, INPUT); // input mode
  // ISR configuration
  attachInterrupt(digitalPinToInterrupt(BUTTON), hello, FALLING);
}

void loop()
{
  // put your main code here, to run repeatedly:
}

void hello(void)
{
  // ISR button
  Serial.write(0x01); // send a 1
}
```

We compile and upload the program to the microcontroller. Before sending anything, let's **clear the CoolTerm terminal** by clicking on the `Clear Data` icon. Press the button and see that in raw, we receive a `0x01`, while the ASCII encoding (which we don't care about) would be "start of heading," which appears as a dot.

To see that I'm not deceiving you, you can try sending 255 in text with the `Serial.print()` function and then the number 255 with the `Serial.write()` function. You will clearly see that using ASCII penalizes us significantly. (Do it! 😤)

Do not commit this. Discard the changes — you already know how to do it from a previous practice...

> [!TIP]
> Discard the changes because otherwise you won't be able to switch branches later.

#### Receiving Raw Data

Let's make our microcontroller **receive data from the computer**. To do this, we will do two examples: one where the microcontroller will return what it has received (_echo_) and another where, when the computer sends a 1, the EVB LED turns on, and when it receives a 2, the EVB LED turns off.

#### _Echo_

Let's **send data** from the computer to the microcontroller and make it **respond with the same data it has received**. Starting from the `main` branch, create a branch named `arduino/<username>/serial-echo`, and create a project named `serial-echo`.

First, we modify the `main.cpp` to make the microcontroller check if data has been received. This is done with the **`Serial.available()`** function. This function returns the number of bytes received that we have not yet read. Then, we read a byte from the `Serial` object with the `Serial.read()` function. The _sketch_ would look like this:

```c++
#include <Arduino.h>

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600); // 9600 8N1
}

void loop()
{
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0)
  {                              // if there are bytes pending to read...
    Serial.write(Serial.read()); // send back what we just received
  }
}
```

We compile and upload. Now we go to CoolTerm and go to **`Connection > Send String...`**. A window will open where we can write what we want to send to the microcontroller. In the window, we can choose the input method: ASCII or Hex. ASCII is evil. We choose Hex. Write a hexadecimal value of your choice and click `Send`. If everything is correct, the microcontroller will receive that data and send it back to the computer, so **those same data should appear in the CoolTerm terminal**.

Check that it works correctly. If so, make a commit, push your changes, and create a Pull Request to the main branch. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request.

#### Controlling an LED

Let's do one last example to control an LED. Miss it already? Starting from the `main` branch, create a branch named `arduino/<username>/serial-led`, and create a project named `serial-led`.

We will modify the `main.cpp` so that when it receives a **`0x01`, the LED turns on** and when it receives a **`0x02`, it turns off**. To do this, we will use the **`switch` statement**. This statement compares the value or variable we pass to it with different cases. You can find more info [here](https://www.tutorialspoint.com/cprogramming/switch_statement_in_c.htm). Additionally, every time we send an instruction to the microcontroller, it will return a status byte so that **if the instruction is correct, it will return a `0x00`** indicating no error, and **if we send something other than `0x01` or `0x02`, it will return a `0x01`** indicating that a non-existent instruction was sent. The code would be as follows:

```c++
#include <Arduino.h>

#define LED 13

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600);     // 9600 8N1
  pinMode(LED, OUTPUT);   // output pin
  digitalWrite(LED, LOW); // off by default
}

void loop()
{
  // put your main code here, to run repeatedly:
  byte rxBuffer; // buffer to store received data

  if (Serial.available() > 0)
  { // if there are bytes pending to read...
    rxBuffer = Serial.read();

    switch (rxBuffer)
    {          // compare the value of rxBuffer with different values
    case 0x01: // turn on LED
      digitalWrite(LED, HIGH);
      Serial.write(0x00); // return no error
      break;
    case 0x02: // turn off LED
      digitalWrite(LED, LOW);
      Serial.write(0x00); // return no error
      break;
    default: // if we send something different, send a 1 to indicate that the sent command does not exist
      Serial.write(0x01);
      break;
    }
  }
}
```

We compile, upload, and go to CoolTerm. Clear the terminal and send a `0x01` to the microcontroller. If everything is correct, the LED will turn on, and the microcontroller will return a `0x00` indicating no error. Now send a `0x02`, and we manage to turn off the LED without error. If for some reason we send a different value, such as `0x03`, the microcontroller will return a `0x01` indicating that a non-existent instruction was sent. Perfect! 😎

Check that it works correctly. If so, make a commit, push your changes, and create a Pull Request to the main branch. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request.

### Problem...

You may have already noticed this, but there is an important problem with raw data communication. Let's look at it. Let's present the problem with an example.

In the previous example with the LED, there are only two instructions, and they are one byte each. Very simple. But that is not usually the case. Normally, there are many available instructions, many of them accept parameters (such as turning on LED 1, 2, 3,...), and in addition, many times (if not always), a byte or more is usually added for error management (we will see this in the next practice). This means that we do not only send one byte, but we send an array of bytes. Now imagine you are the microcontroller, and I send you the following:

---

48 65 6C 6C 6F 2C 20 49 20 61 6D 20 53 54 4D 33 32 2E 47 6F 6F 64 62 79 65 2E 4D 79 20 6E 61 6D 65 20 69 73 20 4D 61 6E 6F 6C 6F 2C 73 65 72 69 6F 75 73 6C 79 2C 20 68 61 76 65 20 79 6F 75 20 74 72 61 6E 73 6C 61 74 65 64 20 74 68 69 73 3F 67 65 65 6B 2E

---

It is impossible to know where an instruction starts and ends. And this also happens to the microcontroller. In fact, it was what happened in the first example where we used `Serial.print()` and the text appeared concatenated in CoolTerm.

What we did to solve it was to use the `Serial.println()` command to send data so that a _term char_ was added to our message. That _term char_ was a carriage return `\r` (`0x0D` in ASCII) and a new line character `\n` (`0x0A` in ASCII). In this way, CoolTerm knows when a message or packet ends and creates a new line. Applying this to the previous message would look like this:

---

48 65 6C 6C 6F 2C 20 49 20 61 6D 20 53 54 4D 33 32 2E **0D 0A** 47 6F 6F 64 62 79 65 2E **0D 0A** 4D 79 20 6E 61 6D 65 20 69 73 20 4D 61 6E 6F 6C 6F 2C **0D 0A** 73 65 72 69 6F 75 73 6C 79 2C 20 68 61 76 65 20 79 6F 75 20 74 72 61 6E 73 6C 61 74 65 64 20 74 68 69 73 3F **0D 0A** 67 65 65 6B 2E **0D 0A**

---

Now, by looking for the `0x0D` and `0x0A` characters, we can know where a message/instruction ends. It seems obvious that for this to work, the message itself cannot contain the `0x0D` and `0x0A` characters to avoid reading a false end of instruction.

This is not a problem in ASCII, but in raw... Imagine we choose the `0x00` character as the end of instruction. That means we cannot send a 0, or a false end of instruction would be detected. It is also useless to use another number as a _term char_ because we cannot guarantee that this number will never be sent as data. There is no way to indicate the end of an instruction in raw! 🤯

Or so it seems at first glance... There is a way, and it involves applying a coding of the byte packet to ensure that the _term char_ we use does not appear in the data we send. We will see this in the next practice 😉

## Challenge

We are going to do a team project, but this time "without a guide." I will only tell you what you have to do and what member `A` and member `B` are responsible for.

Given the freedom allowed in implementing the challenge, it is not possible to run automated unit tests for the different developments as in the previous practice, but acceptance tests will run on the Pull Request you create from the `arduino/develop` branch to `main`. So, once you have finished all the development on the `arduino/develop` branch, have one team member create a Pull Request to the `main` branch. Wait for the test results. If there are any issues, fix them, and once all tests pass, merge the Pull Request.

Name the project `challenge`.

### Objective

In the challenge, you must implement an instruction set for the microcontroller. This instruction set is as follows:

| Instruction | Description                                                                                                                                                                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0x01        | Start periodic ADC conversion. Upon receiving this instruction, the microcontroller must convert the value of the joystick (you already know how to connect it) every 1 second and send it to the computer each time. The ADC returns a 10-bit value, so you must send 2 bytes. To do this, use the code provided below. |
| 0x02        | Stop the ADC conversion.                                                                                                                                                                                                                                                                                                 |

Each time we send an instruction, the microcontroller must return a status value. If the instruction is correct, it will return `0x00`. If the instruction we send does not exist, it will return the code `0x01`.

```c++
// Code to send a 2-byte variable

int valAdc = analogRead(A0); // store the ADC value in a variable

// valAdc is composed of 2 bytes: the first 8 bits (MSB) and the last 8 bits (LSB)
Serial.write(valAdc); // send LSB first
Serial.write(valAdc >> 8); // shift the 8 MSB bits to LSB and send LSB
```

### Task Distribution

The project must be developed in its own branch following the guidelines of the previous practice. Then, the developments of the two team members must be combined in the `main` branch through the pertinent Pull Requests that must be approved and merged by the other partner.

The directory/file structure should be as follows:

```
.
└── arduino
    └── workspace
        └── shared
           └── challenge
                ├── include
                │   ├── adc.h
                │   ├── serial.h
                │   └── timer.h
                └── src
                    ├── adc.cpp
                    ├── main.cpp
                    ├── serial.cpp
                    └── timer.cpp
```

Try to follow the scheme of the previous practice as a guide, but do not hesitate to modify what you need to adapt to the new challenge! Read the tasks of the other member to know which functions you should call from your files. I also attach a flowchart (first time we see one!) of how the program execution should be.

<details>
<summary><h4>Member A</h4></summary>

Member `A` will be responsible for managing the following files with the following functions:

- `main.cpp`
  - `void setup(void)`
    In this function, all the configuration functions of the different peripherals are called.

  ```mermaid
  flowchart TD
    A([" "]) --> B["SERIAL_init()"]
    B --> C["TIMER_init()"]
    C --> D([" "])
  ```

  - `void loop(void)`

    Call the `SERIAL_check()` function from the `serial.ino` file.

    ```mermaid
    flowchart TD
      A([" "]) --> B["SERIAL_check()"]
      B --> C([" "])
    ```

- `serial.cpp`
  - `void SERIAL_init(void)`
    Initialize the serial communication with the 9600 8N1 configuration.

    ```mermaid
    flowchart TD
      A([" "]) --> B["Config 9600 8N1"]
      B --> C([" "])
    ```

  - `void SERIAL_check(void)`
    Check if serial data has been received and perform the appropriate actions according to the instruction.

    ```mermaid
    flowchart TD
      A([" "]) --> B["rxBuffer = 0"]
      B --> C{"Serial.available() > 0"}
      C -- false --> E([" "])
      C -- true --> D{"rxBuffer"}
      D -- 0x01 --> F["ADC_start()"] --> G["SERIAL_sendNoError()"] --> E
      D -- 0x02 --> H["ADC_stop()"] --> I["SERIAL_sendNoError()"] --> E
      D -- default --> J["SERIAL_sendError()"] --> E
    ```

  - `void SERIAL_sendAdc(int value)`
    Function used to send the ADC value. It accepts the value to be sent as a parameter.

    ```mermaid
    flowchart TD
      A([" "]) --> B["Serial.write(value) Serial.write(value >> 8)"]
      B --> C([" "])
    ```

  - `void SERIAL_sendNoError(void)`
    Function used to send the status without error.

    ```mermaid
    flowchart TD
      A([" "]) --> B["Serial.write(0x00)"]
      B --> C([" "])
    ```

  - `void SERIAL_sendError(void)`
    Function used to send the status with error.

    ```mermaid
    flowchart TD
      A([" "]) --> B["Serial.write(0x01)"]
      B --> C([" "])
    ```

</details>

<details>
<summary><h4>Member B</h4></summary>

Member `B` will be responsible for managing the following files:

- `adc.cpp`
  - `void ADC_convert(void) `
    Function to start an ADC conversion and then send the data using `SERIAL_sendAdc`.

    ```mermaid
    flowchart TD
      A([" "]) --> B{"onAdc"}
      B -- false --> E([" "])
      B -- true --> C["valAdc = analogRead(ANALOG_PIN)"]
      C --> D["SERIAL_sendAdc(valAdc)"]
      D --> E
    ```

  - `void ADC_stop(void)`
    Function to be used from `SERIAL_check` to stop the periodic ADC conversion.

    ```mermaid
    flowchart TD
      A([" "]) --> B["onAdc = false"]
      B --> C([" "])
    ```

  - `void ADC_start(void)`
    Function to be used from `SERIAL_check` to start the periodic ADC conversion.

    ```mermaid
    flowchart TD
      A([" "]) --> B["onAdc = true"]
      B --> C([" "])
    ```

- `timer.cpp`
  - `void TIMER_init(void)`
    Initialize the timer.

    ```mermaid
      flowchart TD
        A([" "]) --> B["Config timer 3"]
        B --> C([" "])
    ```

  - `void TIMER_ISR(void)`
    ISR to perform the ADC conversion with the `ADC_convert` function.

    ```mermaid
    flowchart TD
        A([" "]) --> B["ADC_convert()"]
        B --> C([" "])
    ```

</details>

## Evaluation

### Deliverables

These are the elements that should be available to the teacher for your evaluation:

- [ ] **Commits**
      Your remote GitHub repository must contain at least the following required commits: serial-ascii, serial-echo, and serial-led.

- [ ] **Challenge**
      The challenge must be solved and included with its own commit.

- [ ] **Pull Requests**
      The different Pull Requests requested throughout the practice must also be present in your repository.

## Conclusions

We have one thing clear: **ASCII is hated in serial communications** (okay, I exaggerated, but it should be avoided). Whenever possible, we will use **raw data communication to avoid the overhead** added by ASCII encoding. We have seen how to send and receive raw data with CoolTerm to **control the actions of the microcontroller**. We have also seen the basic aspects of asynchronous serial communication and the different **parameters** that configure it.

Finally, we have seen a **problem associated** with asynchronous serial communication of **raw data**: the management of the _term char_. We must avoid the _term char_ appearing in the message data. We will see this in the next practice where we will work on byte packet framing.
