#!/usr/bin/perl
# ------------------------------------------------------------
#  counter.cgi  -  シンプルなアクセスカウンター（JSONを返す）
#
#   counter.cgi        … 現在の数を返す（数えない）
#   counter.cgi?inc=1  … 1増やしてから返す
#
#   返り値: {"total":123,"today":4}
#   データは同じフォルダの counter.dat に保存（無ければ自動作成）
#   パーミッション: counter.cgi は 755（ロリポップは 700 でも可）
# ------------------------------------------------------------
use strict;
use warnings;
use Fcntl qw(:flock O_RDWR O_CREAT);

my $DATA = 'counter.dat';

# --- 日本時間の日付 ---
my @t = gmtime(time + 9 * 3600);
my $today = sprintf('%04d-%02d-%02d', $t[5] + 1900, $t[4] + 1, $t[3]);

# --- inc=1 のときだけ数える ---
my $qs  = $ENV{QUERY_STRING} || '';
my $inc = ($qs =~ /(?:^|&)inc=1(?:&|$)/) ? 1 : 0;

my ($total, $day, $daycount) = (0, $today, 0);

if (sysopen(my $fh, $DATA, O_RDWR | O_CREAT, 0600)) {
    flock($fh, LOCK_EX);
    my $line = <$fh>;
    if (defined $line && $line =~ /^(\d+)\t(\d{4}-\d{2}-\d{2})\t(\d+)/) {
        ($total, $day, $daycount) = ($1, $2, $3);
    }
    if ($day ne $today) { ($day, $daycount) = ($today, 0); }
    if ($inc) {
        $total++;
        $daycount++;
        seek($fh, 0, 0);
        truncate($fh, 0);
        print {$fh} "$total\t$day\t$daycount\n";
    }
    flock($fh, LOCK_UN);
    close($fh);
}

print "Content-Type: application/json; charset=utf-8\n";
print "Cache-Control: no-store\n";
print "X-Content-Type-Options: nosniff\n\n";
print qq({"total":$total,"today":$daycount}\n);
