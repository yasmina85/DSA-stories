package source_code;
import java.util.ArrayList;
import com.cybozu.labs.langdetect.LangDetectException;
import com.cybozu.labs.langdetect.Detector;
import com.cybozu.labs.langdetect.DetectorFactory;
import com.cybozu.labs.langdetect.Language;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class DetectLanguage {
    public static void init() throws LangDetectException {
		String profileDirectory = "source_code/profiles";
        DetectorFactory.loadProfile(profileDirectory);
    }
    public static boolean  detect(String text) throws LangDetectException {
         Detector detector = DetectorFactory.create();
         detector.append(text);
         if("en".equalsIgnoreCase(detector.detect())){
			 return true;
         }
		 return false;
     }
	public static void main(String[] args) throws IOException, LangDetectException{
		System.out.println("Detecting English pages");
		init();
		if(args.length < 2){
			System.out.println("Usage exclude_non_english [timemap_file] [collection_directory]");
			System.exit(1);
		}
		
		String timemap_file = args[0];
	    String collection_directory = args[1];
		String text_dir = collection_directory+"/text/";
		BufferedReader timemap_reader = new BufferedReader(new FileReader(timemap_file));

		String en_timemap_file = collection_directory+"/timemap_english.txt";
		BufferedWriter en_timemap_writer = new BufferedWriter(new FileWriter(en_timemap_file));
		
		while(timemap_reader.ready()){
			
			String line = timemap_reader.readLine();
			String[] fields = line.split("\t");
			String uri_id = fields[0];
			String dt = fields[1];
			File textFile = new File(text_dir+uri_id+"/"+dt+".txt");
			if(!textFile.exists()){
				continue;
			}
			
			BufferedReader reader = new BufferedReader(new FileReader(textFile));
			StringBuffer textBuffer = new StringBuffer();
			while(reader.ready()){
				textBuffer.append(reader.readLine()+"\n");
			}
			reader.close();
			try {
				if(detect(textBuffer.toString()) ){
					en_timemap_writer.write(line+"\n");
				}
			} catch (LangDetectException e){
				e.printStackTrace();
			}
		}
		en_timemap_writer.close();
		timemap_reader.close();
	}	
}
