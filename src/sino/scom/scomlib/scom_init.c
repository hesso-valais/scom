
#include "scom_init.h"

void initscom_data_link_module(void);

void initscom()
{
    printf ("--> 1\r\n");
    (void) Py_InitModule("scom", NULL);
    initscom_data_link_module();
    printf ("--> 11\r\n");
}

void PyInit_scom()
{
    printf ("--> 2\r\n");
    (void) Py_InitModule("scom", NULL);
}

void scom_test01()
{
    printf ("--> 3\r\n");
}