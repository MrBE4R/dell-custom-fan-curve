# Dell custom fan curve 

Python project to set a custom fan curve for Dell PowerEdge servers.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project has been tested on :
 - Rocky Linux 8.6 with Python 3.6.8.
 - TrueNAS-SCALE 22.02.2 with Python 3.9.2

You will need to install `ipmitool` and `smartmontools`.

This has been tested on R630 and R730XD.

### Installing

To get this up and running you just need to do the following :

* Clone the repo
```bash
cd /opt
git clone https://github.com/MrBE4R/dell-custom-fan-curve
```
* Edit config.ini with you values
```bash
cp /opt/dell-custom-fan-curve/config.ini.example /opt/dell-custom-fan-curve/config.ini
$EDITOR /opt/dell-custom-fan-curve/config.ini
```
* Install service and start it
```bash
cp /opt/dell-custom-fan-curve/dell-custom-fan-curve.services /usr/lib/systemd/system/dell-custom-fan-curve.services
systemctl daemon-reload
systemctl enable --now dell-custom-fan-curve.services
systemctl status dell-custom-fan-curve.services
```

## Built With

* [Python](https://www.python.org/)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Jean-François GUILLAUME (Jeff MrBear)** - *Initial work* - [MrBE4R](https://github.com/MrBE4R)

See also the list of [contributors](https://github.com/MrBE4R/dell-custom-fan-curve/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
