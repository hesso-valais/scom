
#ifndef SCOM_INIT_H
#define SCOM_INIT_H

#include "Python.h"

/*
 * Links:
 * - http://techtonik.rainforce.org/2007/12/entrypoint-instructions-to-using-c-code.html
 */

PyMODINIT_FUNC initscom();
PyMODINIT_FUNC PyInit_scom();


PyMODINIT_FUNC scom_test01();

#endif // SCOM_INIT_H