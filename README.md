# DfAnalyzer Transparent

DfAnalyzer Transparent, also known as dfa-tr, is a tool designed to assist with collecting prospective and retrospective provenance in Python scripts without the need for manual instrumentation.

This tool allows users to provide a Python script that they want to collect provenance from, and it automatically adds the necessary instrumentations to collect the provenance and sends it to the DfAnalyzer tool.

DfAnalyzer Transparent was proposed and developed as a partial requirement for the E-Science course taught by Professor [Vanessa Braganholo](https://github.com/braganholo) for the graduate course at the Computation Institute of the Fluminense Federal University.

## Installation and Usage

1. Install and run [DfAnalyzer](https://github.com/UFFeScience/DfAnalyzer/tree/master/DfAnalyzer).
1. Clone this repository.
2. Place your Python script in the "src" directory.
3. Provide your script as an argument to the "main.py" script and run it using the following command:

```
python main.py <your-python-script>.py [arg...]
```

## Viewing the Collected Provenance

After installing all the dependencies for DfAnalyzer, connect to MonetDB using the following command:

```
mclient -h localhost -p 50000 -d dataflow_analyzer -u monetdb
```

In this version of the tool, provenance is collected at the function level. To view the provenance, use the following commands:

For input functions:

```
select * from i_<function_name>
```

For output functions:

```
select * from o_<function_name>
```

## License

MIT License

Copyright (c) 2022 Line Version

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
