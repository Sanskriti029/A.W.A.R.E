#include <iostream>
using namespace std;

int main() {
    double electricity, water, transport;
    cin >> electricity >> water >> transport;

    // Simple estimation formula (arbitrary factors for demo)
    double footprint = (electricity * 0.5) + (water * 0.002) + (transport * 0.21);

    cout << footprint; // Flask will capture and show in UI
    return 0;
}
