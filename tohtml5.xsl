<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- The last attribute below is the HTML5 compatibility attribute -->
<xsl:output method="html" encoding="utf-8" indent="yes" doctype-system="about:legacy-compat"/>

<xsl:template match="/rss/channel">
<html>
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
    <title><xsl:value-of select="title"/></title>
    <link rel="alternate" type="application/rss+xml" title="RSS" href="index.xml"/>
    <style>
body { font-family: "Libertine", Palatino, "Palatino Linotype", "Book Antiqua", Georgia, "Times New Roman", serif }
a { color: #ac2734; text-decoration: underline }
audio { height: 3ex; vertical-align: middle }
    </style>
</head>
<body>
    <h1><xsl:value-of select="title"/></h1>
    <xsl:apply-templates select="item">
        <xsl:sort select="link"/>
    </xsl:apply-templates>
</body>
</html>
</xsl:template>

<xsl:template match="item">
    <xsl:variable name="currentdate">
        <xsl:call-template name="pubDate">
            <xsl:with-param name="text" select="pubDate"/>
        </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="previousdate">
        <xsl:choose>
            <xsl:when test="position() = 1"></xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="pubDate">
                    <!-- Yes, it is indeed the following sibling, because items are sorted in reverse order -->
                    <xsl:with-param name="text" select="following-sibling::item/pubDate"/>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:if test="$currentdate != $previousdate">
        <time>
            <xsl:attribute name="datetime"><xsl:value-of select="$currentdate"/></xsl:attribute>
            <xsl:value-of select="$currentdate"/>
        </time>
    </xsl:if>
    <p>
        <audio>
            <xsl:attribute name="controls"></xsl:attribute>
            <xsl:attribute name="preload">none</xsl:attribute>
            <source>
                <xsl:attribute name="src"><xsl:value-of select="enclosure/@url"/></xsl:attribute>
                <xsl:attribute name="type"><xsl:value-of select="enclosure/@type"/></xsl:attribute>
            </source>
        </audio>
        <xsl:text> </xsl:text>
        <xsl:value-of select="title"/>
        <xsl:text> </xsl:text>
        <a>
            <xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute>
            <xsl:attribute name="target">_blank</xsl:attribute>
            Link
        </a>
    </p>
</xsl:template>

<xsl:template name="pubDate">
    <xsl:param name="text"/>
    <xsl:variable name="monthName"><xsl:value-of select="substring($text, 9, 3)"/></xsl:variable>
    <xsl:value-of select="substring($text, 13, 4)"/>
    <xsl:text>-</xsl:text>
    <xsl:choose>
        <xsl:when test="$monthName = 'Jan'">01</xsl:when>
        <xsl:when test="$monthName = 'Feb'">02</xsl:when>
        <xsl:when test="$monthName = 'Mar'">03</xsl:when>
        <xsl:when test="$monthName = 'Apr'">04</xsl:when>
        <xsl:when test="$monthName = 'May'">05</xsl:when>
        <xsl:when test="$monthName = 'Jun'">06</xsl:when>
        <xsl:when test="$monthName = 'Jul'">07</xsl:when>
        <xsl:when test="$monthName = 'Aug'">08</xsl:when>
        <xsl:when test="$monthName = 'Sep'">09</xsl:when>
        <xsl:when test="$monthName = 'Oct'">10</xsl:when>
        <xsl:when test="$monthName = 'Nov'">11</xsl:when>
        <xsl:when test="$monthName = 'Dec'">12</xsl:when>
    </xsl:choose>
    <xsl:text>-</xsl:text>
    <xsl:value-of select="substring($text, 6, 2)"/>
</xsl:template>

</xsl:stylesheet>

