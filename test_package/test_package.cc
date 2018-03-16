#include <stdio.h>
#include <json-c/json.h>

int main()
{
	printf("Successfully initialized json-c version %s.\n", json_c_version());
	return 0;
}
