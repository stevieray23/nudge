$sites = @(
    @{name="dr-carl-kreitz"; url="https://dr-carl-kreitz.de/impressum"},
    @{name="dr-carl-kreitz2"; url="https://dr-carl-kreitz.de/impressum/"},
    @{name="loewenzahnaerzte"; url="https://www.loewenzahnaerzte.de/impressum/"},
    @{name="zahnarztbraunschweig-wagner"; url="https://www.zahnarztbraunschweig-wagner.de/impressum/"},
    @{name="zahnarztbraunschweig-wagner2"; url="https://www.zahnarztbraunschweig-wagner.de/datenschutz"},
    @{name="drlauer"; url="https://drlauer.de/impressum/"},
    @{name="drlauer2"; url="https://www.drlauer.de/impressum/"},
    @{name="zahnarzt-artmax"; url="https://www.zahnarzt-artmax.de/impressum/"},
    @{name="zahnarzt-artmax2"; url="https://zahnarzt-artmax.de/impressum/"},
    @{name="zahnarzt-in-bs"; url="https://www.zahnarzt-in-braunschweig.de/impressum/"},
    @{name="zahnarzt-ac"; url="https://www.zahnarzt.ac/impressum/"},
    @{name="zahnarztpraxis-frobenius"; url="https://www.zahnarztpraxis-frobenius.de/impressum/"},
    @{name="zats-schulze"; url="https://www.zats.de/impressum/"},
    @{name="zats-schulze2"; url="https://www.zats.de"},
    @{name="zahnarzt-hilger"; url="https://www.loewenzahnaerzte.de/impressum"},
    @{name="hzw-kiel"; url="https://www.hzw-kiel.de/impressum/"},
    @{name="hzw-kiel2"; url="https://hzw-kiel.de/impressum/"},
    @{name="hzw-kiel3"; url="https://www.hzw.de/impressum/"},
    @{name="praxis-hilger"; url="https://www.zahnarzthilger.de/impressum/"},
    @{name="crott"; url="https://www.crott.de/impressum/"},
    @{name="crott2"; url="https://www.zahnarzt-crott.de/impressum/"},
    @{name="drunkem"; url="https://www.drunkemoeller.de/impressum/"},
    @{name="hertzog"; url="https://www.dent-a-la-carte.de/impressum/"},
    @{name="hertzog2"; url="https://www.hertzog-zahnarzt.de/impressum/"},
    @{name="liske"; url="https://www.zahnarzt-liske.de/impressum/"},
    @{name="liske2"; url="https://www.praxis-liske.de/impressum/"},
    @{name="guzinski"; url="https://www.zahnarzt-guzinski.de/impressum/"},
    @{name="brandt-halle"; url="https://www.zahnarzt-brandt-halle.de/impressum/"},
    @{name="brandt-halle2"; url="https://www.praxis-brandt-halle.de/impressum/"},
    @{name="lenk"; url="https://www.zahnarzt-lenk.de/impressum/"},
    @{name="lenk2"; url="https://www.praxis-lenk.de/impressum/"},
    @{name="hantschel"; url="https://www.hantschel-zahnarzt.de/impressum/"},
    @{name="golbs"; url="https://www.golbs-zahnarzt.de/impressum/"},
    @{name="golbs2"; url="https://www.dr-golbs.de/impressum/"},
    @{name="wittig"; url="https://www.zahnarzt-wittig.de/impressum/"},
    @{name="haertel"; url="https://www.zahnarzt-haertel.de/impressum/"},
    @{name="obst"; url="https://www.zahnarzt-obst.de/impressum/"},
    @{name="wolff-dresden"; url="https://www.zahnarzt-wolff.de/impressum/"},
    @{name="venus"; url="https://www.zahnarzt-venus.de/impressum/"},
    @{name="laubner"; url="https://www.kieferorthopaedie-laubner.de/impressum/"},
    @{name="laubner2"; url="https://www.laubner-kfo.de/impressum/"},
    @{name="luck"; url="https://www.zahnarzt-luck.de/impressum/"},
    @{name="hagen"; url="https://www.zahnarzt-hagen.de/impressum/"},
    @{name="alldent"; url="https://www.alldent-dresden.de/impressum/"},
    @{name="luedicke"; url="https://www.zahnarzt-luedicke.de/impressum/"},
    @{name="buchmann"; url="https://www.zahnarzt-buchmann.de/impressum/"},
    @{name="heider"; url="https://www.zahnarzt-heider.de/impressum/"},
    @{name="silber"; url="https://www.zahnarzt-silber.de/impressum/"},
    @{name="boehme"; url="https://www.zahnarzt-boehme.de/impressum/"},
    @{name="peikert"; url="https://www.zahnarzt-peikert.de/impressum/"},
    @{name="goetze"; url="https://www.zahnarzt-goetze.de/impressum/"},
    @{name="bartsch"; url="https://www.zahnarzt-bartsch.de/impressum/"},
    @{name="eismann"; url="https://www.zahnarzt-eismann.de/impressum/"},
    @{name="kutaibah"; url="https://www.zahnarzt-kutaibah.de/impressum/"},
    @{name="prochnow"; url="https://www.zahnarzt-prochnow.de/impressum/"},
    @{name="metzler"; url="https://www.zahnarzt-metzler.de/impressum/"},
    @{name="deckert"; url="https://www.zahnarzt-deckert.de/impressum/"},
    @{name="blitz"; url="https://www.zahnarzt-blitz.de/impressum/"},
    @{name="kuehnoel"; url="https://www.zahnarzt-kuehnoel.de/impressum/"},
    @{name="mann"; url="https://www.zahnarzt-mann-dresden.de/impressum/"},
    @{name="kempe"; url="https://www.zahnarzt-kempe.de/impressum/"},
    @{name="appel-aachen"; url="https://www.zahnarzt-appel.de/impressum/"}
)

$results = @()
foreach ($site in $sites) {
    $status = "unknown"
    $content = ""
    try {
        $response = Invoke-WebRequest -Uri $site.url -Method HEAD -TimeoutSec 10 -UseBasicParsing 2>$null
        $status = $response.StatusCode
    } catch {
        $status = "ERROR: " + $_.Exception.Message
    }
    $results += [PSCustomObject]@{
        name = $site.name
        url = $site.url
        status = $status
    }
    Write-Host "$($site.name): $status"
}

$results | Format-Table -AutoSize
