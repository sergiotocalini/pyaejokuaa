# Copyright 1999-2012 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI="3"
PYTHON_DEPEND="*"

inherit python subversion

DESCRIPTION="pyAeJokuaa is a pluggable application to store passwords securely."
HOMEPAGE="http://code.google.com/p/pyaejokuaa/"
ESVN_REPO_URI="http://pyaejokuaa.googlecode.com/svn/trunk/"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 x86"
IUSE="+anate +gtk hesapea morandu qt"

DEPEND="net-zope/zope-interface
	dev-python/paramiko
	dev-python/configobj
	dev-python/elixir
	dev-python/pygobject
	dev-python/pytz"

RDEPEND="${DEPEND}
	 gtk? ( dev-python/pygtk )
	 qt? ( dev-python/PyQt4 ) "


src_unpack() {
	subversion_src_unpack
}

src_install() {
	insinto /usr/share/${PN}
	doins -r * || die "doins failed"

	fperms a+x /usr/share/${PN}/pyAeJokuaa || die "fperms failed"
	dosym /usr/share/${PN}/pyAeJokuaa /usr/bin/pyAeJokuaa || die "dosym failed"
}

pkg_postinst() {
	python_mod_optimize /usr/share/${PN}
	einfo "If you want to report bugs, open a new ticket at http://code.google.com/p/pyaejokuaa/issues/entry"
}

pkg_postrm() {
	python_mod_cleanup /usr/share/${PN}
}
